from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from firebase_admin import auth
import uuid
from datetime import datetime
from typing import Optional, List
import csv
import io

from src.database import get_db
from src.models import User, AuditLog
from src.security.auth import get_current_user
from src.schemas.audit import AuditLogRead

router = APIRouter(prefix="/admin", tags=["admin"])


class ImpersonationRequest(BaseModel):
    reason: str


async def require_admin(user: User = Depends(get_current_user)):
    if not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


@router.post("/impersonate/{patient_id}")
async def impersonate_patient(
    patient_id: str, req: ImpersonationRequest, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    try:
        pid = uuid.UUID(patient_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid patient ID format")

    # Log Break Glass
    audit = AuditLog(
        actor_user_id=admin.id,
        action_type="IMPERSONATE",
        resource_type="PATIENT",
        resource_id=pid,
        changes_json={"reason": req.reason},
    )
    db.add(audit)
    await db.commit()

    # Generate Custom Token
    try:
        additional_claims = {"act_as": str(pid), "impersonator_id": str(admin.id), "role": "PATIENT"}
        custom_token = auth.create_custom_token(str(pid), additional_claims)

        if isinstance(custom_token, bytes):
            custom_token = custom_token.decode("utf-8")

        return {"token": custom_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")


# =============================================================================
# Audit Log Endpoints
# =============================================================================

class AuditLogListResponse(BaseModel):
    items: List[AuditLogRead]
    total: int
    page: int
    page_size: int


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    action_type: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[uuid.UUID] = Query(None),
    actor_user_id: Optional[uuid.UUID] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List audit logs with optional filtering.
    Requires admin privileges.
    """
    # Log the access to audit logs
    access_audit = AuditLog(
        actor_user_id=admin.id,
        action_type="READ",
        resource_type="AUDIT_LOG",
        resource_id=admin.id,
        changes_json={"search_params": {
            "action_type": action_type,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id else None,
            "actor_user_id": str(actor_user_id) if actor_user_id else None,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
        }}
    )
    db.add(access_audit)
    
    # Build query
    stmt = select(AuditLog)
    
    if action_type:
        stmt = stmt.where(AuditLog.action_type == action_type)
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
    if resource_id:
        stmt = stmt.where(AuditLog.resource_id == resource_id)
    if actor_user_id:
        stmt = stmt.where(AuditLog.actor_user_id == actor_user_id)
    if date_from:
        stmt = stmt.where(AuditLog.occurred_at >= date_from)
    if date_to:
        stmt = stmt.where(AuditLog.occurred_at <= date_to)
    
    # Count total
    count_result = await db.execute(stmt)
    total = len(count_result.scalars().all())
    
    # Paginate
    offset = (page - 1) * page_size
    stmt = stmt.order_by(desc(AuditLog.occurred_at)).offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    await db.commit()
    
    return AuditLogListResponse(
        items=logs,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/audit-logs/export")
async def export_audit_logs(
    action_type: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[uuid.UUID] = Query(None),
    actor_user_id: Optional[uuid.UUID] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Export audit logs as CSV.
    """
    # Log export
    export_audit = AuditLog(
        actor_user_id=admin.id,
        action_type="EXPORT",
        resource_type="AUDIT_LOG",
        resource_id=admin.id,
    )
    db.add(export_audit)
    
    # Build query
    stmt = select(AuditLog)
    
    if action_type:
        stmt = stmt.where(AuditLog.action_type == action_type)
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
    if resource_id:
        stmt = stmt.where(AuditLog.resource_id == resource_id)
    if actor_user_id:
        stmt = stmt.where(AuditLog.actor_user_id == actor_user_id)
    if date_from:
        stmt = stmt.where(AuditLog.occurred_at >= date_from)
    if date_to:
        stmt = stmt.where(AuditLog.occurred_at <= date_to)
    
    stmt = stmt.order_by(desc(AuditLog.occurred_at))
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    await db.commit()
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "occurred_at", "action_type", "resource_type", "resource_id", "actor_user_id", "ip_address", "user_agent", "impersonator_id", "changes_json"])
    
    for log in logs:
        writer.writerow([
            str(log.id),
            log.occurred_at.isoformat() if log.occurred_at else "",
            log.action_type,
            log.resource_type,
            str(log.resource_id),
            str(log.actor_user_id) if log.actor_user_id else "",
            log.ip_address or "",
            log.user_agent or "",
            str(log.impersonator_id) if log.impersonator_id else "",
            str(log.changes_json) if log.changes_json else "",
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
    )


@router.get("/audit-logs/{log_id}", response_model=AuditLogRead)
async def get_audit_log(
    log_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific audit log entry.
    """
    stmt = select(AuditLog).where(AuditLog.id == log_id)
    result = await db.execute(stmt)
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return log


# =============================================================================
# Super Admin Endpoints
# =============================================================================

from src.models import Organization
from sqlalchemy import func as sql_func

class OrganizationAdminRead(BaseModel):
    id: uuid.UUID
    name: str
    member_count: int
    patient_count: int
    subscription_status: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    items: List[OrganizationAdminRead]
    total: int
    page: int
    page_size: int


class UserAdminRead(BaseModel):
    id: uuid.UUID
    email: str
    display_name: Optional[str]
    is_super_admin: bool
    locked_until: Optional[datetime]
    failed_login_attempts: int
    last_login_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    items: List[UserAdminRead]
    total: int
    page: int
    page_size: int


class SystemHealth(BaseModel):
    db_status: str
    redis_status: str
    worker_status: str
    metrics: dict


class OrganizationUpdate(BaseModel):
    is_active: Optional[bool] = None
    subscription_status: Optional[str] = None


class UserAdminUpdate(BaseModel):
    is_super_admin: Optional[bool] = None


@router.get("/super-admin/organizations", response_model=OrganizationListResponse)
async def list_all_organizations(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all organizations across the platform."""
    stmt = select(Organization).where(Organization.deleted_at.is_(None))
    
    if search:
        stmt = stmt.where(Organization.name.ilike(f"%{search}%"))
    
    # Count total
    count_result = await db.execute(stmt)
    total = len(count_result.scalars().all())
    
    # Paginate
    offset = (page - 1) * page_size
    stmt = stmt.order_by(Organization.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    orgs = result.scalars().all()
    
    return OrganizationListResponse(
        items=orgs,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/super-admin/organizations/{org_id}", response_model=OrganizationAdminRead)
async def get_organization_detail(
    org_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed organization info."""
    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return org


@router.patch("/super-admin/organizations/{org_id}", response_model=OrganizationAdminRead)
async def update_organization(
    org_id: uuid.UUID,
    update: OrganizationUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update organization (suspend, activate, etc.)."""
    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    # Audit
    audit = AuditLog(
        actor_user_id=admin.id,
        action_type="UPDATE",
        resource_type="ORGANIZATION",
        resource_id=org.id,
        changes_json=update_data,
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(org)
    return org


@router.get("/super-admin/users", response_model=UserListResponse)
async def list_all_users(
    search: Optional[str] = Query(None),
    is_locked: Optional[bool] = Query(None),
    is_super_admin: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users across the platform."""
    stmt = select(User).where(User.deleted_at.is_(None))
    
    if search:
        stmt = stmt.where(User.email.ilike(f"%{search}%"))
    if is_locked is not None:
        if is_locked:
            stmt = stmt.where(User.locked_until.isnot(None))
        else:
            stmt = stmt.where(User.locked_until.is_(None))
    if is_super_admin is not None:
        stmt = stmt.where(User.is_super_admin == is_super_admin)
    
    # Count total
    count_result = await db.execute(stmt)
    total = len(count_result.scalars().all())
    
    # Paginate
    offset = (page - 1) * page_size
    stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/super-admin/users/{user_id}/unlock")
async def unlock_user(
    user_id: uuid.UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Unlock a locked user account."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.locked_until = None
    user.failed_login_attempts = 0
    
    # Audit
    audit = AuditLog(
        actor_user_id=admin.id,
        action_type="UNLOCK",
        resource_type="USER",
        resource_id=user.id,
    )
    db.add(audit)
    
    await db.commit()
    return {"success": True, "message": f"User {user.email} unlocked"}


@router.patch("/super-admin/users/{user_id}", response_model=UserAdminRead)
async def update_user_admin(
    user_id: uuid.UUID,
    update: UserAdminUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update user (toggle super admin, etc.)."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Audit
    audit = AuditLog(
        actor_user_id=admin.id,
        action_type="UPDATE",
        resource_type="USER",
        resource_id=user.id,
        changes_json=update_data,
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/super-admin/system", response_model=SystemHealth)
async def get_system_health(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get system health status."""
    from src.config import settings
    import redis.asyncio as redis
    
    # Check DB
    db_status = "healthy"
    try:
        await db.execute(select(1))
    except Exception:
        db_status = "unhealthy"
    
    # Check Redis
    redis_status = "healthy"
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
    except Exception:
        redis_status = "unhealthy"
    
    # Metrics (basic counts)
    user_count = await db.scalar(select(sql_func.count()).select_from(User))
    org_count = await db.scalar(select(sql_func.count()).select_from(Organization))
    
    return SystemHealth(
        db_status=db_status,
        redis_status=redis_status,
        worker_status="unknown",  # Would need ARQ inspection
        metrics={
            "total_users": user_count or 0,
            "total_organizations": org_count or 0,
        }
    )
