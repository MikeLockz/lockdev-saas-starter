from uuid import UUID

from fastapi import Depends, HTTPException, Path
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db, tenant_id_ctx
from src.models.organizations import Organization, OrganizationMember
from src.models.users import User
from src.security.auth import get_current_user


class OrgAccess:
    def __init__(self, role_required: str = None):
        self.role_required = role_required

    async def __call__(
        self,
        org_id: UUID = Path(...),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> OrganizationMember:
        # Super Admins can access any organization with implicit ADMIN privileges
        if current_user.is_super_admin:
            # Verify the organization exists
            org_stmt = select(Organization).where(Organization.id == org_id)
            org_result = await db.execute(org_stmt)
            org = org_result.scalar_one_or_none()

            if not org:
                raise HTTPException(status_code=404, detail="Organization not found")

            # Set RLS context for tenant
            tenant_id_ctx.set(str(org_id))
            if db.in_transaction():
                await db.execute(text("SELECT set_config('app.current_tenant_id', :tid, false)"), {"tid": str(org_id)})

            # Return a synthetic OrganizationMember with ADMIN role for Super Admins
            # Note: This is not persisted, just used for authorization
            synthetic_member = OrganizationMember(organization_id=org_id, user_id=current_user.id, role="ADMIN")
            return synthetic_member

        # Query membership for regular users
        stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id, OrganizationMember.user_id == current_user.id
        )
        result = await db.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            raise HTTPException(status_code=403, detail="Not a member of this organization")

        # Check role if required
        if self.role_required and self.role_required == "ADMIN" and member.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Organization admin access required")
            # Can extend for other roles hierarchy if needed

        # Set RLS context for tenant
        tenant_id_ctx.set(str(org_id))
        if db.in_transaction():
            await db.execute(text("SELECT set_config('app.current_tenant_id', :tid, false)"), {"tid": str(org_id)})

        return member


get_current_org_member = OrgAccess()
require_org_admin = OrgAccess(role_required="ADMIN")
