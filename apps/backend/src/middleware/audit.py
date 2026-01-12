"""
Audit Middleware for READ Access Logging

This middleware intercepts GET requests to sensitive routes and logs
READ_ACCESS events to the audit_logs table for HIPAA compliance.
"""

import re
import uuid as uuid_lib

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.database import get_db
from src.models import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log READ access to sensitive routes.

    Logs GET requests to:
    - /api/staff/*
    - /api/patients/*
    """

    # Patterns for routes that require audit logging
    SENSITIVE_PATTERNS = [
        re.compile(r"^/api/staff/(?P<resource_id>[^/]+)"),
        re.compile(r"^/api/patients/(?P<resource_id>[^/]+)"),
    ]

    async def dispatch(self, request: Request, call_next):
        # Only audit GET requests
        if request.method == "GET":
            await self._maybe_log_read_access(request)

        response = await call_next(request)
        return response

    async def _maybe_log_read_access(self, request: Request) -> None:
        """
        Check if the request matches a sensitive pattern and log if needed.
        """
        path = request.url.path

        for pattern in self.SENSITIVE_PATTERNS:
            match = pattern.match(path)
            if match:
                await self._log_read_access(request, match)
                break

    async def _log_read_access(self, request: Request, match: re.Match) -> None:
        """
        Log a READ_ACCESS event to the audit_logs table.

        This is done as a background task to avoid blocking the request.
        """
        try:
            # Extract resource information
            resource_id_str = match.group("resource_id")

            # Determine resource type from path
            if "/staff/" in request.url.path:
                resource_type = "staff"
            elif "/patients/" in request.url.path:
                resource_type = "patient"
            else:
                resource_type = "unknown"

            # Get user information from request state (set by auth middleware)
            actor_user_id = getattr(request.state, "user_id", None)
            organization_id = getattr(request.state, "organization_id", None)
            impersonator_id = getattr(request.state, "impersonator_id", None)

            # Get IP and User-Agent
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

            # Parse resource_id as UUID
            try:
                resource_id = uuid_lib.UUID(resource_id_str)
            except ValueError:
                # If not a valid UUID, skip logging
                return

            # Create audit log entry (background task)
            # Note: We use request.app.state to access the database session factory
            async for db in get_db():
                audit_log = AuditLog(
                    actor_user_id=actor_user_id,
                    organization_id=organization_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    action_type="READ",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    impersonator_id=impersonator_id,
                    changes_json=None,  # No changes for READ operations
                )

                db.add(audit_log)
                await db.commit()
                break  # Only need one iteration

        except Exception as e:
            # Log error but don't block the request
            import structlog

            logger = structlog.get_logger(__name__)
            logger.error("audit_event_logging_failed", error=str(e))
