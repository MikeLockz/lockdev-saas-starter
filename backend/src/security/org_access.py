from uuid import UUID
from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db, tenant_id_ctx
from src.models.organizations import OrganizationMember
from src.security.auth import get_current_user
from src.models.users import User

class OrgAccess:
    def __init__(self, role_required: str = None):
        self.role_required = role_required

    async def __call__(
        self,
        org_id: UUID = Path(...),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> OrganizationMember:
        # Query membership
        stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == current_user.id
        )
        result = await db.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            raise HTTPException(status_code=403, detail="Not a member of this organization")
        
        # Check role if required
        if self.role_required:
            if self.role_required == "ADMIN" and member.role != "ADMIN":
                raise HTTPException(status_code=403, detail="Organization admin access required")
            # Can extend for other roles hierarchy if needed

        # Set RLS context for tenant
        tenant_id_ctx.set(str(org_id))
        
        return member

get_current_org_member = OrgAccess()
require_org_admin = OrgAccess(role_required="ADMIN")
