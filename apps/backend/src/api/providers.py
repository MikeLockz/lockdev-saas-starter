from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.organizations import OrganizationMember
from src.models.profiles import Provider
from src.models.users import User
from src.schemas.providers import (
    PaginatedProviders,
    ProviderCreate,
    ProviderListItem,
    ProviderRead,
    ProviderUpdate,
)
from src.security.org_access import get_current_org_member, require_org_admin

router = APIRouter()


@router.post("", response_model=ProviderRead, status_code=status.HTTP_201_CREATED)
async def create_provider(
    org_id: UUID,
    provider_data: ProviderCreate,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a provider profile for a user (promotes user to provider role).
    Requires admin access.
    """
    now = datetime.now(UTC)

    # Verify user exists
    user_stmt = select(User).where(User.id == provider_data.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if NPI is already used in this org
    if provider_data.npi_number:
        existing_stmt = (
            select(Provider)
            .where(Provider.organization_id == org_id)
            .where(Provider.npi_number == provider_data.npi_number)
            .where(Provider.deleted_at is None)
        )
        existing_result = await db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A provider with this NPI already exists in this organization",
            )

    # Check if user already has a provider profile in this org
    existing_provider_stmt = (
        select(Provider)
        .where(Provider.organization_id == org_id)
        .where(Provider.user_id == provider_data.user_id)
        .where(Provider.deleted_at is None)
    )
    existing_provider_result = await db.execute(existing_provider_stmt)
    if existing_provider_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This user already has a provider profile in this organization"
        )

    # Create Provider
    provider = Provider(
        user_id=provider_data.user_id,
        organization_id=org_id,
        npi_number=provider_data.npi_number,
        specialty=provider_data.specialty,
        license_number=provider_data.license_number,
        license_state=provider_data.license_state,
        dea_number=provider_data.dea_number,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(provider)
    await db.commit()
    await db.refresh(provider)

    return ProviderRead(
        id=provider.id,
        user_id=provider.user_id,
        organization_id=provider.organization_id,
        npi_number=provider.npi_number,
        specialty=provider.specialty,
        license_number=provider.license_number,
        license_state=provider.license_state,
        dea_number=provider.dea_number,
        state_licenses=provider.state_licenses or [],
        is_active=provider.is_active,
        created_at=provider.created_at,
        updated_at=provider.updated_at,
        user_email=user.email,
        user_display_name=user.display_name,
    )


@router.get("", response_model=PaginatedProviders)
async def list_providers(
    org_id: UUID,
    specialty: str | None = Query(None, description="Filter by specialty"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    List all providers in the organization.
    """
    # Base query
    base_query = (
        select(Provider, User)
        .join(User, Provider.user_id == User.id)
        .where(Provider.organization_id == org_id)
        .where(Provider.deleted_at is None)
    )

    # Apply filters
    if specialty:
        base_query = base_query.where(Provider.specialty.ilike(f"%{specialty}%"))

    if is_active is not None:
        base_query = base_query.where(Provider.is_active == is_active)
    else:
        # Default to active only
        base_query = base_query.where(Provider.is_active)

    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    paginated_query = base_query.order_by(User.display_name, User.email).offset(offset).limit(limit)
    result = await db.execute(paginated_query)
    rows = result.all()

    items = []
    for provider, user in rows:
        items.append(
            ProviderListItem(
                id=provider.id,
                user_id=provider.user_id,
                npi_number=provider.npi_number,
                specialty=provider.specialty,
                is_active=provider.is_active,
                user_email=user.email,
                user_display_name=user.display_name,
            )
        )

    return PaginatedProviders(items=items, total=total, limit=limit, offset=offset)


@router.get("/{provider_id}", response_model=ProviderRead)
async def get_provider(
    org_id: UUID,
    provider_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    Get full provider details.
    """
    stmt = (
        select(Provider, User)
        .join(User, Provider.user_id == User.id)
        .where(Provider.id == provider_id)
        .where(Provider.organization_id == org_id)
        .where(Provider.deleted_at is None)
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    provider, user = row

    return ProviderRead(
        id=provider.id,
        user_id=provider.user_id,
        organization_id=provider.organization_id,
        npi_number=provider.npi_number,
        specialty=provider.specialty,
        license_number=provider.license_number,
        license_state=provider.license_state,
        dea_number=provider.dea_number,
        state_licenses=provider.state_licenses or [],
        is_active=provider.is_active,
        created_at=provider.created_at,
        updated_at=provider.updated_at,
        user_email=user.email,
        user_display_name=user.display_name,
    )


@router.patch("/{provider_id}", response_model=ProviderRead)
async def update_provider(
    org_id: UUID,
    provider_id: UUID,
    provider_update: ProviderUpdate,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update provider fields. Requires admin access.
    """
    stmt = (
        select(Provider)
        .options(selectinload(Provider.user))
        .where(Provider.id == provider_id)
        .where(Provider.organization_id == org_id)
        .where(Provider.deleted_at is None)
    )
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    # Check NPI uniqueness if changing
    update_data = provider_update.model_dump(exclude_unset=True)
    if "npi_number" in update_data and update_data["npi_number"] != provider.npi_number:
        existing_stmt = (
            select(Provider)
            .where(Provider.organization_id == org_id)
            .where(Provider.npi_number == update_data["npi_number"])
            .where(Provider.id != provider_id)
            .where(Provider.deleted_at is None)
        )
        existing_result = await db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A provider with this NPI already exists in this organization",
            )

    # Apply updates
    for field, value in update_data.items():
        setattr(provider, field, value)

    provider.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(provider)

    # Get user for response
    user_stmt = select(User).where(User.id == provider.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one()

    return ProviderRead(
        id=provider.id,
        user_id=provider.user_id,
        organization_id=provider.organization_id,
        npi_number=provider.npi_number,
        specialty=provider.specialty,
        license_number=provider.license_number,
        license_state=provider.license_state,
        dea_number=provider.dea_number,
        state_licenses=provider.state_licenses or [],
        is_active=provider.is_active,
        created_at=provider.created_at,
        updated_at=provider.updated_at,
        user_email=user.email,
        user_display_name=user.display_name,
    )


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    org_id: UUID,
    provider_id: UUID,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a provider (set is_active=false and deleted_at).
    Requires admin access.
    """
    stmt = (
        select(Provider)
        .where(Provider.id == provider_id)
        .where(Provider.organization_id == org_id)
        .where(Provider.deleted_at is None)
    )
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    now = datetime.now(UTC)
    provider.is_active = False
    provider.deleted_at = now
    provider.updated_at = now

    await db.commit()
    return None
