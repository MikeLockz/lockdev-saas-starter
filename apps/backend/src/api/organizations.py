from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models import User
from src.models.invitations import Invitation
from src.models.organizations import Organization, OrganizationMember
from src.schemas.invitations import InvitationCreate, InvitationRead
from src.schemas.organizations import MemberRead, OrganizationCreate, OrganizationRead, OrganizationUpdate
from src.security.auth import get_current_user
from src.security.org_access import get_current_org_member, require_org_admin
from src.worker import enqueue_task

router = APIRouter()


@router.get("", response_model=list[OrganizationRead])
async def list_organizations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    List all organizations the current user is a member of.
    """
    stmt = (
        select(Organization)
        .join(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .where(Organization.deleted_at is None)
        .where(OrganizationMember.deleted_at is None)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=OrganizationRead)
async def create_organization(
    org_create: OrganizationCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Create a new organization and make the current user an ADMIN.
    """
    now = datetime.now(UTC)

    # Create Organization
    org = Organization(
        name=org_create.name,
        tax_id=org_create.tax_id,
        settings_json=org_create.settings_json,
        created_at=now,
        updated_at=now,
        member_count=1,  # Initial member
    )
    db.add(org)
    await db.flush()  # Get ID

    # Create Membership
    member = OrganizationMember(
        organization_id=org.id, user_id=current_user.id, role="ADMIN", created_at=now, updated_at=now
    )
    db.add(member)

    await db.commit()
    await db.refresh(org)
    return org


@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(
    org_id: UUID, member: OrganizationMember = Depends(get_current_org_member), db: AsyncSession = Depends(get_db)
):
    """
    Get organization details. Requires membership.
    """
    # Member dependency already loaded membership, so we just need org.
    # But OrganizationMember model has relationship to Organization, we can use that if eager loaded
    # or query again. Let's query again to be safe and ensure we get the latest org state which matches schema.

    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one()  # Should exist if member exists
    return org


@router.patch("/{org_id}", response_model=OrganizationRead)
async def update_organization(
    org_id: UUID,
    org_update: OrganizationUpdate,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update organization. Requires ADMIN role.
    """
    from src.validators import validate_timezone

    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one()

    update_data = org_update.model_dump(exclude_unset=True)

    # Validate timezone if provided
    if "timezone" in update_data and update_data["timezone"] and not validate_timezone(update_data["timezone"]):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid timezone: {update_data['timezone']}. Must be a valid IANA timezone.",
        )

    for field, value in update_data.items():
        setattr(org, field, value)

    org.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(org)
    return org


@router.get("/{org_id}/members", response_model=list[MemberRead])
async def list_members(
    org_id: UUID, member: OrganizationMember = Depends(get_current_org_member), db: AsyncSession = Depends(get_db)
):
    """
    List members of an organization. Requires membership.
    """
    stmt = (
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.deleted_at is None)
    )
    result = await db.execute(stmt)
    members = result.scalars().all()

    # Enrich with user details if needed, schema expects email/display_name
    # Since we defined MemberRead with these fields, and OrganizationMember doesn't have them directly (they are on User),
    # we should likely join User or rely on lazy loading if configured.
    # OrganizationMember has `user` relationship. Pydantic `from_attributes` works with ORM objects if they are loaded.
    # Best to eager load user.

    stmt = (
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.deleted_at is None)
    )
    result = await db.execute(stmt)
    members = result.scalars().all()

    # We need to map User fields to MemberRead flattened fields.
    # Pydantic v2 configuration might not flatten automatically from relationship unless we alias paths.
    # Alternatively, we construct the response manually or update schema.

    # Let's map manually to be safe.
    response = []
    for m in members:
        response.append(
            MemberRead(
                id=m.id,
                user_id=m.user_id,
                organization_id=m.organization_id,
                email=m.user.email,
                display_name=m.user.display_name or m.user.full_name,
                role=m.role,
                created_at=m.created_at,
            )
        )
    return response


# Story 8.2 is "Invitations", so create/invite goes there.
@router.post("/{org_id}/invitations", response_model=InvitationRead)
async def create_invitation(
    org_id: UUID,
    invite_data: InvitationCreate,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite a user to the organization. Requires ADMIN role.
    """
    # Check if email is already a member
    stmt = (
        select(OrganizationMember)
        .join(User)
        .where(OrganizationMember.organization_id == org_id)
        .where(User.email == invite_data.email)
        .where(OrganizationMember.deleted_at is None)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member of this organization"
        )

    # Check for pending invitation
    stmt = (
        select(Invitation)
        .where(Invitation.organization_id == org_id)
        .where(Invitation.email == invite_data.email)
        .where(Invitation.status == "PENDING")
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation already pending for this email")

    # Create Invitation
    token = token_urlsafe(32)
    now = datetime.now(UTC)
    expires_at = now + timedelta(hours=48)  # 48 hour expiry

    invitation = Invitation(
        organization_id=org_id,
        email=invite_data.email,
        role=invite_data.role,
        token=token,
        invited_by_user_id=member.user_id,
        status="PENDING",
        created_at=now,
        expires_at=expires_at,
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)

    # Enqueue Email
    # We need org name for the email
    org_stmt = select(Organization).where(Organization.id == org_id)
    org_result = await db.execute(org_stmt)
    org = org_result.scalar_one()

    await enqueue_task("send_invitation_email", email=invitation.email, token=invitation.token, org_name=org.name)

    return invitation


@router.get("/{org_id}/invitations", response_model=list[InvitationRead])
async def list_invitations(
    org_id: UUID, member: OrganizationMember = Depends(require_org_admin), db: AsyncSession = Depends(get_db)
):
    """
    List pending invitations. Requires ADMIN role.
    """

    stmt = select(Invitation).where(Invitation.organization_id == org_id).where(Invitation.status == "PENDING")
    result = await db.execute(stmt)
    return result.scalars().all()
