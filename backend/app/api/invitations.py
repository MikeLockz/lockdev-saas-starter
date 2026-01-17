import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.models.invitation import Invitation
from app.models.organization import OrganizationMember
from app.models.user import User
from app.schemas.invitations import InvitationRead

router = APIRouter()


@router.get(
    "/{token}",
    response_model=InvitationRead,
    summary="Get invitation details",
    description=(
        "Retrieves the details of an organization invitation using its secure "
        "token. Validates that the invitation is still pending and not expired."
    ),
)
async def get_invitation(token: str, db: AsyncSession = Depends(get_db)):
    """
    Get invitation details by token.
    """
    stmt = select(Invitation).where(Invitation.token == token)
    result = await db.execute(stmt)
    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
        )

    if invite.status != "pending" or invite.expires_at < datetime.datetime.now(
        datetime.UTC
    ):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation expired or already used",
        )

    return invite


@router.post(
    "/{token}/accept",
    summary="Accept an invitation",
    description=(
        "Accepts a pending organization invitation. Validates the user's email "
        "and creates an OrganizationMember record with the specified role."
    ),
)
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Accept an invitation.
    """
    stmt = select(Invitation).where(Invitation.token == token)
    result = await db.execute(stmt)
    invite = result.scalar_one_or_none()

    if not invite or invite.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
        )

    # Verify email matches (optional but recommended)
    if invite.email != current_user.email:
        raise HTTPException(status_code=403, detail="Email mismatch")

    # Create membership
    member = OrganizationMember(
        organization_id=invite.organization_id,
        user_id=current_user.id,
        role=invite.role,
    )
    db.add(member)

    # Update invitation
    invite.status = "accepted"
    invite.accepted_at = datetime.datetime.now(datetime.UTC)

    await db.commit()
    return {"message": "Invitation accepted"}
