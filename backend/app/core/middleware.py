import json
import time
import uuid
from contextvars import ContextVar

import sentry_sdk
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import current_tenant_id, current_user_id
from app.core.redis import redis_client

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
logger = structlog.get_logger(__name__)


HTTP_200_OK = 200
HTTP_300_MULTIPLE_CHOICES = 300


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    [API-008] Ensures idempotency for state-changing requests using X-Idempotency-Key.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in ["POST", "PATCH", "PUT"]:
            return await call_next(request)

        idempotency_key = request.headers.get("X-Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        # Scoped by user to prevent collisions between different users
        user_id = current_user_id.get() or "anonymous"
        redis_key = f"idempotency:{user_id}:{idempotency_key}"

        cached = await redis_client.get(redis_key)
        if cached:
            data = json.loads(cached)
            logger.info("idempotency_hit", key=idempotency_key, user_id=user_id)
            return Response(
                content=data["body"],
                status_code=data["status_code"],
                headers=data.get("headers", {}),
                media_type=data.get("media_type"),
            )

        response: Response = await call_next(request)

        # Only cache successful responses to allow retries on transient errors
        if HTTP_200_OK <= response.status_code < HTTP_300_MULTIPLE_CHOICES:
            cache_data = {
                "body": "",  # Body caching disabled to avoid stream issues
                "status_code": response.status_code,
                "media_type": response.media_type,
                "headers": dict(response.headers),
            }
            # Cache for 24 hours
            await redis_client.setex(redis_key, 86400, json.dumps(cache_data))

        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        request.state.request_id = request_id

        # Bind to structlog
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # MON-006: Propagate to Sentry
        sentry_sdk.set_tag("request_id", request_id)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    [API-012] Logs request completion with status and duration.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        response: Response = await call_next(request)
        duration = time.perf_counter() - start_time

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=f"{duration:.4f}s",
            request_id=request.state.request_id,
        )
        return response


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Reset contextvars at start of request
        u_token = current_user_id.set(None)
        t_token = current_tenant_id.set(None)
        try:
            return await call_next(request)
        finally:
            current_user_id.reset(u_token)
            current_tenant_id.reset(t_token)


class ReadAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # 200 is status.HTTP_200_OK
        if request.method == "GET" and response.status_code == 200:  # noqa: PLR2004
            path = request.url.path
            if path.startswith(("/api/patients/", "/api/staff/")):
                import structlog

                logger = structlog.get_logger("audit")
                logger.info("READ_ACCESS", path=path, user_id=current_user_id.get())

        return response
