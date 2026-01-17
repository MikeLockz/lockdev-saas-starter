import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import current_tenant_id, current_user_id

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
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
