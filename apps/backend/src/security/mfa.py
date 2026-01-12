"""
MFA (Multi-Factor Authentication) enforcement module.

Implements P1-002: MFA enforcement for privileged roles accessing PHI.
Required by HIPAA compliance for strong authentication.
"""

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User
from src.models.organizations import OrganizationMember
from src.security.auth import get_current_user

# Roles that require MFA to access PHI
PRIVILEGED_ROLES = {"STAFF", "PROVIDER", "ADMIN"}


async def require_mfa(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Require MFA for privileged roles accessing PHI.

    This dependency should be used on all PHI-related endpoints to enforce
    that users with STAFF, PROVIDER, or ADMIN roles have MFA enabled.

    Raises:
        HTTPException: 403 if user has privileged role but MFA is not enabled

    Returns:
        User: The current authenticated user
    """
    # Get user's roles from organization memberships
    stmt = select(OrganizationMember.role).where(
        OrganizationMember.user_id == user.id,
        OrganizationMember.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    user_roles = {row[0] for row in result.fetchall()}

    # Check if user has any privileged roles
    if user_roles & PRIVILEGED_ROLES:
        # Require MFA for privileged roles
        if not user.mfa_enabled:
            raise HTTPException(
                status_code=403,
                detail="MFA is required for your role. Please enable MFA in account settings before accessing patient data.",
            )

    return user
