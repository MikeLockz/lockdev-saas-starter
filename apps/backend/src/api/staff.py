from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.organizations import OrganizationMember
from src.models.profiles import Staff
from src.models.users import User
from src.schemas.providers import (
    PaginatedStaff,
    StaffCreate,
    StaffListItem,
    StaffRead,
    StaffUpdate,
)
from src.security.org_access import get_current_org_member, require_org_admin

router = APIRouter()


@router.post("", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
async def create_staff(
    org_id: UUID,
    staff_data: StaffCreate,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a staff profile for a user.
    Requires admin access.
    """
    now = datetime.now(UTC)

    # Verify user exists
    user_stmt = select(User).where(User.id == staff_data.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if user already has a staff profile in this org
    existing_staff_stmt = (
        select(Staff)
        .where(Staff.organization_id == org_id)
        .where(Staff.user_id == staff_data.user_id)
        .where(Staff.deleted_at.is_(None))
    )
    existing_staff_result = await db.execute(existing_staff_stmt)
    if existing_staff_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This user already has a staff profile in this organization"
        )

    # Create Staff
    staff = Staff(
        user_id=staff_data.user_id,
        organization_id=org_id,
        job_title=staff_data.job_title,
        department=staff_data.department,
        employee_id=staff_data.employee_id,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(staff)
    await db.commit()
    await db.refresh(staff)

    return StaffRead(
        id=staff.id,
        user_id=staff.user_id,
        organization_id=staff.organization_id,
        job_title=staff.job_title,
        department=staff.department,
        employee_id=staff.employee_id,
        is_active=staff.is_active,
        created_at=staff.created_at,
        updated_at=staff.updated_at,
        user_email=user.email,
        user_display_name=user.display_name,
    )


@router.get("", response_model=PaginatedStaff)
async def list_staff(
    org_id: UUID,
    department: str | None = Query(None, description="Filter by department"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    List all staff members in the organization.
    """
    # Base query
    base_query = (
        select(Staff, User)
        .join(User, Staff.user_id == User.id)
        .where(Staff.organization_id == org_id)
        .where(Staff.deleted_at.is_(None))
    )

    # Apply filters
    if department:
        base_query = base_query.where(Staff.department.ilike(f"%{department}%"))

    if is_active is not None:
        base_query = base_query.where(Staff.is_active == is_active)
    else:
        # Default to active only
        base_query = base_query.where(Staff.is_active)

    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    paginated_query = base_query.order_by(User.display_name, User.email).offset(offset).limit(limit)
    result = await db.execute(paginated_query)
    rows = result.all()

    items = []
    for staff, user in rows:
        items.append(
            StaffListItem(
                id=staff.id,
                user_id=staff.user_id,
                job_title=staff.job_title,
                department=staff.department,
                is_active=staff.is_active,
                user_email=user.email,
                user_display_name=user.display_name,
            )
        )

    return PaginatedStaff(items=items, total=total, limit=limit, offset=offset)


@router.get("/{staff_id}", response_model=StaffRead)
async def get_staff(
    org_id: UUID,
    staff_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    Get full staff details.
    """
    stmt = (
        select(Staff, User)
        .join(User, Staff.user_id == User.id)
        .where(Staff.id == staff_id)
        .where(Staff.organization_id == org_id)
        .where(Staff.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")

    staff, user = row

    return StaffRead(
        id=staff.id,
        user_id=staff.user_id,
        organization_id=staff.organization_id,
        job_title=staff.job_title,
        department=staff.department,
        employee_id=staff.employee_id,
        is_active=staff.is_active,
        created_at=staff.created_at,
        updated_at=staff.updated_at,
        user_email=user.email,
        user_display_name=user.display_name,
    )


@router.patch("/{staff_id}", response_model=StaffRead)
async def update_staff(
    org_id: UUID,
    staff_id: UUID,
    staff_update: StaffUpdate,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update staff fields. Requires admin access.
    """
    stmt = (
        select(Staff)
        .options(selectinload(Staff.user))
        .where(Staff.id == staff_id)
        .where(Staff.organization_id == org_id)
        .where(Staff.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    staff = result.scalar_one_or_none()

    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")

    # Apply updates
    update_data = staff_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(staff, field, value)

    staff.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(staff)

    # Get user for response
    user_stmt = select(User).where(User.id == staff.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one()

    return StaffRead(
        id=staff.id,
        user_id=staff.user_id,
        organization_id=staff.organization_id,
        job_title=staff.job_title,
        department=staff.department,
        employee_id=staff.employee_id,
        is_active=staff.is_active,
        created_at=staff.created_at,
        updated_at=staff.updated_at,
        user_email=user.email,
        user_display_name=user.display_name,
    )


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(
    org_id: UUID,
    staff_id: UUID,
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a staff member (set is_active=false and deleted_at).
    Requires admin access.
    """
    stmt = (
        select(Staff)
        .where(Staff.id == staff_id)
        .where(Staff.organization_id == org_id)
        .where(Staff.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    staff = result.scalar_one_or_none()

    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")

    now = datetime.now(UTC)
    staff.is_active = False
    staff.deleted_at = now
    staff.updated_at = now

    await db.commit()
    return None
