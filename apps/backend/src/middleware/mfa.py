"""
MFA Enforcement Middleware.

Ensures that users with privileged roles (STAFF, PROVIDER, ADMIN) have MFA enabled
before accessing protected endpoints. This is defense-in-depth against bypassing
frontend MFA checks via direct API access.

HIPAA Compliance: Ensures authentication controls cannot be circumvented.
"""

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Routes that are exempt from MFA enforcement
# These allow users to set up MFA or authenticate
EXEMPT_PATH_PREFIXES = (
    "/api/v1/users/me/mfa",  # MFA setup/verify endpoints
    "/api/v1/auth",  # Authentication endpoints
    "/health",  # Health checks
    "/docs",  # API documentation
    "/redoc",  # API documentation
    "/openapi.json",  # OpenAPI schema
)

# Roles that MUST have MFA enabled to access protected endpoints
ROLES_REQUIRING_MFA = {"STAFF", "PROVIDER", "ADMIN"}


class MFAEnforcementMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces MFA for privileged users.

    After authentication middleware sets request.state.user, this middleware
    checks if the user has a role that requires MFA and whether MFA is enabled.
    If MFA is not enabled, access is denied with 403 Forbidden.
    """

    async def dispatch(self, request: Request, call_next):
        # Always allow exempt paths (MFA setup, auth, health checks)
        if request.url.path.startswith(EXEMPT_PATH_PREFIXES):
            return await call_next(request)

        # If authentication hasn't run yet, let the request through
        # (auth middleware will handle 401 if needed)
        user = getattr(request.state, "user", None)
        if user is None:
            return await call_next(request)

        # Check if user has a role that requires MFA
        user_role = self._get_user_role(user)
        if user_role not in ROLES_REQUIRING_MFA:
            return await call_next(request)

        # Check if MFA is enabled
        mfa_enabled = getattr(user, "mfa_enabled", False)
        if not mfa_enabled:
            logger.warning(
                f"MFA enforcement: User {user.id} (role={user_role}) attempted "
                f"to access {request.url.path} without MFA enabled"
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "MFA is required for your account",
                    "code": "MFA_REQUIRED",
                },
            )

        return await call_next(request)

    def _get_user_role(self, user) -> str | None:
        """
        Determine the user's highest-privilege role.

        Checks organization memberships to find if user is STAFF, PROVIDER, or ADMIN.
        Returns None if user has no privileged role.
        """
        # Super admins are always considered to have a privileged role
        if getattr(user, "is_super_admin", False):
            return "ADMIN"

        # Check organization memberships for privileged roles
        memberships = getattr(user, "memberships", [])
        for membership in memberships:
            role = getattr(membership, "role", None)
            if role in ROLES_REQUIRING_MFA:
                return role

        return None
