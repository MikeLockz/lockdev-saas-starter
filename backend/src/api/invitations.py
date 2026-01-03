from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.security.auth import get_current_user
from src.models import User
from src.models.organizations import Organization, OrganizationMember
from src.models.invitations import Invitation
from src.schemas.invitations import InvitationRead

router = APIRouter()

@router.get("/{token}", response_model=InvitationRead)
async def get_invitation(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get invitation details from token. Public endpoint.
    """
    stmt = select(Invitation).where(Invitation.token == token)
    result = await db.execute(stmt)
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
        
    if invitation.status != "PENDING":
        raise HTTPException(status_code=410, detail="Invitation is no longer valid")
        
    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = "EXPIRED" # Update status just in case? Or just return 410
        await db.commit() # Ideally we update it
        raise HTTPException(status_code=410, detail="Invitation has expired")

    return invitation

@router.post("/{token}/accept", response_model=InvitationRead)
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Accept an invitation. Requires user to be logged in.
    """
    stmt = select(Invitation).where(Invitation.token == token)
    result = await db.execute(stmt)
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
        
    if invitation.status != "PENDING":
        raise HTTPException(status_code=410, detail="Invitation is no longer valid")
        
    now = datetime.now(timezone.utc)
    if invitation.expires_at < now:
        invitation.status = "EXPIRED"
        await db.commit()
        raise HTTPException(status_code=410, detail="Invitation has expired")
        
    # Verify email matches current user? 
    # Usually usage: Invites are by email. Should we enforce the logged in user matches the email?
    # Yes, for security, unless we allow "claim" behavior.
    # Check if user email matches invitation email.
    if invitation.email.lower() != current_user.email.lower():
         raise HTTPException(
             status_code=400, 
             detail="This invitation was sent to a different email address. Please login with that email."
         )

    # Check if already member
    stmt = (
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == invitation.organization_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.deleted_at == None)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
         # Already member, just mark invite accepted
         invitation.status = "ACCEPTED"
         invitation.accepted_at = now
         await db.commit()
         return invitation

    # Create membership
    member = OrganizationMember(
        organization_id=invitation.organization_id,
        user_id=current_user.id,
        role=invitation.role,
        created_at=now,
        updated_at=now
    )
    db.add(member)
    
    # Update invitation
    invitation.status = "ACCEPTED"
    invitation.accepted_at = now
    
    await db.commit()
    await db.refresh(invitation)
    return invitation
