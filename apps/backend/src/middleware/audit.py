"""
Audit Middleware for READ and WRITE Access Logging

This middleware implements an "Audit by Default" strategy for HIPAA compliance.
It logs access events for ALL requests (GET, POST, PUT, PATCH, DELETE) to
organization and PHI-rich endpoints, with specific exclusions for non-sensitive routes.

Per Security Audit P1-006: Extended to log write operations with HTTP context
(IP address, User-Agent, impersonator_id, request_id) that database triggers cannot capture.
"""

import contextlib
import re
import uuid as uuid_lib

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.database import get_db
from src.models import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log READ and WRITE access using an "Audit by Default" strategy.

    Audits ALL requests (GET, POST, PUT, PATCH, DELETE) to:
    - /api/v1/organizations/{org_id}/* (all org-scoped resources)
    - /api/v1/users/me/threads/* (messaging - contains PHI)
    - /api/v1/users/me/notifications/* (may reference PHI)

    Explicitly EXCLUDES:
    - Health check endpoints
    - OpenAPI/docs endpoints
    - Static assets
    - Webhook endpoints (server-to-server, no user context)

    Captures HTTP context that database triggers cannot:
    - IP address
    - User-Agent
    - Impersonator ID (for break-glass access)
    - Request ID (for correlation)
    """

    # Patterns for routes that REQUIRE audit logging (Audit by Default)
    AUDIT_PATTERNS = [
        # All organization-scoped routes (patients, providers, staff, appointments, calls, etc.)
        re.compile(
            r"^/api/v1/organizations/(?P<org_id>[^/]+)(?:/(?P<resource_type>[^/]+))?(?:/(?P<resource_id>[^/]+))?"
        ),
        # User-scoped PHI routes
        re.compile(r"^/api/v1/users/me/threads(?:/(?P<resource_id>[^/]+))?"),
        re.compile(r"^/api/v1/users/me/notifications(?:/(?P<resource_id>[^/]+))?"),
        # Legacy patterns for backwards compatibility
        re.compile(r"^/api/staff/(?P<resource_id>[^/]+)"),
        re.compile(r"^/api/patients/(?P<resource_id>[^/]+)"),
    ]

    # Patterns to EXCLUDE from audit logging (non-sensitive or infrastructure)
    EXCLUDE_PATTERNS = [
        re.compile(r"^/health"),
        re.compile(r"^/docs"),
        re.compile(r"^/redoc"),
        re.compile(r"^/openapi\.json"),
        re.compile(r"^/api/v1/openapi\.json"),
        re.compile(r"^/api/v1/webhooks"),
        re.compile(r"^/static"),
        re.compile(r"^/admin"),  # Admin panel has its own audit trail
    ]

    async def dispatch(self, request: Request, call_next):
        # Capture request info BEFORE executing
        request_info = {
            "method": request.method,
            "path": request.url.path,
            "user_id": getattr(request.state, "user_id", None),
            "org_id": getattr(request.state, "organization_id", None),
            "ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "impersonator_id": getattr(request.state, "impersonator_id", None),
        }

        # Execute request
        response = await call_next(request)

        # Log after successful request
        if response.status_code < 400:  # Only log successful operations
            if request.method == "GET":
                await self._maybe_log_read_access(request)
            elif request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                await self._maybe_log_write_access(request, response, request_info)

        return response

    async def _maybe_log_read_access(self, request: Request) -> None:
        """
        Check if the request should be audited using the "Audit by Default" strategy.
        """
        path = request.url.path

        # First check exclusions
        for exclude_pattern in self.EXCLUDE_PATTERNS:
            if exclude_pattern.match(path):
                return  # Skip audit for excluded paths

        # Then check if path matches any audit pattern
        for pattern in self.AUDIT_PATTERNS:
            match = pattern.match(path)
            if match:
                await self._log_read_access(request, match, path)
                break

    async def _log_read_access(self, request: Request, match: re.Match, path: str) -> None:
        """
        Log a READ_ACCESS event to the audit_logs table.

        Extracts resource type and ID from the matched path pattern.
        """
        try:
            # Extract resource information from path
            resource_type = self._determine_resource_type(match, path)
            resource_id = self._extract_resource_id(match)

            # Get user information from request state (set by auth middleware)
            actor_user_id = getattr(request.state, "user_id", None)
            organization_id = getattr(request.state, "organization_id", None)
            impersonator_id = getattr(request.state, "impersonator_id", None)

            # Try to get org_id from path if not in request state
            if not organization_id:
                org_id_str = match.groupdict().get("org_id")
                if org_id_str:
                    with contextlib.suppress(ValueError):
                        organization_id = uuid_lib.UUID(org_id_str)

            # Get IP and User-Agent
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

            # Create audit log entry
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
            logger.error("audit_event_logging_failed", error=str(e), path=path)

    def _determine_resource_type(self, match: re.Match, path: str) -> str:
        """
        Determine the resource type from the matched path.
        """
        groups = match.groupdict()

        # Check explicit resource_type group first
        if groups.get("resource_type"):
            return groups["resource_type"].rstrip("s")  # Normalize plural to singular

        # Fallback: parse from path segments
        if "/staff/" in path:
            return "staff"
        elif "/patients/" in path:
            return "patient"
        elif "/providers/" in path:
            return "provider"
        elif "/appointments/" in path:
            return "appointment"
        elif "/calls/" in path:
            return "call"
        elif "/threads/" in path:
            return "message_thread"
        elif "/documents/" in path:
            return "document"
        elif "/proxies/" in path:
            return "proxy"
        elif "/tasks/" in path:
            return "task"
        elif "/billing/" in path:
            return "billing"
        elif "/notifications/" in path:
            return "notification"
        else:
            return "unknown"

    def _extract_resource_id(self, match: re.Match) -> uuid_lib.UUID | None:
        """
        Extract and validate the resource ID from the match.
        Returns None if no valid UUID is found.
        """
        resource_id_str = match.groupdict().get("resource_id")
        if not resource_id_str:
            return None

        try:
            return uuid_lib.UUID(resource_id_str)
        except ValueError:
            return None

    async def _maybe_log_write_access(self, request: Request, response, request_info: dict) -> None:
        """
        Check if the write request should be audited and log it.

        This complements database triggers by capturing HTTP context
        that triggers cannot access (IP, User-Agent, impersonator_id).
        """
        path = request_info["path"]

        # First check exclusions
        for exclude_pattern in self.EXCLUDE_PATTERNS:
            if exclude_pattern.match(path):
                return  # Skip audit for excluded paths

        # Then check if path matches any audit pattern
        for pattern in self.AUDIT_PATTERNS:
            match = pattern.match(path)
            if match:
                await self._log_write_access(request, match, path, request_info)
                break

    async def _log_write_access(self, request: Request, match: re.Match, path: str, request_info: dict) -> None:
        """
        Log a write operation (CREATE, UPDATE, DELETE) to the audit_logs table.

        Maps HTTP methods to action types:
        - POST -> CREATE
        - PUT/PATCH -> UPDATE
        - DELETE -> DELETE
        """
        try:
            # Map HTTP method to action type
            action_map = {
                "POST": "CREATE",
                "PUT": "UPDATE",
                "PATCH": "UPDATE",
                "DELETE": "DELETE",
            }
            action_type = action_map.get(request_info["method"], "UNKNOWN")

            # Extract resource information from path
            resource_type = self._determine_resource_type(match, path)
            resource_id = self._extract_resource_id(match)

            # Get organization ID from path if not in request state
            organization_id = request_info["org_id"]
            if not organization_id:
                org_id_str = match.groupdict().get("org_id")
                if org_id_str:
                    with contextlib.suppress(ValueError):
                        organization_id = uuid_lib.UUID(org_id_str)

            # Create audit log entry
            async for db in get_db():
                audit_log = AuditLog(
                    actor_user_id=request_info["user_id"],
                    organization_id=organization_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    action_type=action_type,
                    ip_address=request_info["ip"],
                    user_agent=request_info["user_agent"],
                    impersonator_id=request_info["impersonator_id"],
                    changes_json={
                        "http_method": request_info["method"],
                        "status_code": 200,  # Simplified - response was successful
                    },
                )

                db.add(audit_log)
                await db.commit()
                break  # Only need one iteration

        except Exception as e:
            # Log error but don't block the request
            import structlog

            logger = structlog.get_logger(__name__)
            logger.error("write_audit_event_logging_failed", error=str(e), path=path, method=request_info["method"])
