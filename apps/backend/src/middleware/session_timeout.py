"""
Session Timeout Middleware for HIPAA Compliance.

Enforces automatic session invalidation after 15 minutes of inactivity
per HIPAA requirement 45 CFR § 164.312(a)(2)(iii).
"""

from datetime import UTC, datetime, timedelta

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.database import get_db
from src.models.sessions import UserSession

logger = structlog.get_logger(__name__)

# HIPAA-compliant idle timeout (15 minutes)
IDLE_TIMEOUT_MINUTES = 15

# Paths that bypass session timeout enforcement
EXEMPT_PATHS = frozenset(
    {
        "/health",
        "/health/deep",
        "/webhooks/stripe",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)


class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce session idle timeout.

    Checks if the user's session has been idle for more than IDLE_TIMEOUT_MINUTES.
    If so, revokes the session and returns HTTP 401.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip enforcement for exempt paths
        path = request.url.path
        if path in EXEMPT_PATHS or path.startswith("/webhooks/"):
            return await call_next(request)

        # Process the request first to allow authentication to set session_id
        response = await call_next(request)

        # After response, check if we need to enforce timeout
        # Note: We check AFTER because session_id is set during auth
        session_id = getattr(request.state, "session_id", None)

        if session_id:
            try:
                async for db in get_db():
                    session = await db.get(UserSession, session_id)
                    if session and session.last_active_at:
                        idle_time = datetime.now(UTC) - session.last_active_at.replace(tzinfo=UTC)
                        if idle_time > timedelta(minutes=IDLE_TIMEOUT_MINUTES):
                            # Revoke the session
                            session.is_revoked = True
                            await db.commit()

                            logger.warning(
                                "session_timeout_enforced",
                                session_id=str(session_id),
                                idle_minutes=idle_time.total_seconds() / 60,
                            )

                            # Return 401 instead of the original response
                            return JSONResponse(
                                status_code=401,
                                content={"detail": "Session expired due to inactivity"},
                            )
                    break
            except Exception as e:
                # Log but don't block the request if session check fails
                logger.error("session_timeout_check_failed", error=str(e))

        return response
