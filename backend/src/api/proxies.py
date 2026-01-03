"""Proxy Management API endpoints."""
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.security.org_access import get_current_org_member
from src.security.auth import get_current_user
from src.models.organizations import OrganizationMember, OrganizationPatient
from src.models.profiles import Patient, Proxy
from src.models.assignments import PatientProxyAssignment
from src.models.users import User
from src.models.audit import AuditLog
from src.schemas.proxies import (
    ProxyAssignmentCreate,
    ProxyAssignmentRead,
    ProxyAssignmentUpdate,
    ProxyPermissions,
    ProxyUserInfo,
    ProxyPatientRead,
    ProxyPatientInfo,
    ProxyListResponse,
)

router = APIRouter()


async def _verify_patient_access(
    org_id: UUID,
    patient_id: UUID,
    db: AsyncSession
) -> OrganizationPatient:
    """Verify patient is enrolled in organization."""
    enrollment_stmt = (
        select(OrganizationPatient)
        .where(OrganizationPatient.organization_id == org_id)
        .where(OrganizationPatient.patient_id == patient_id)
    )
    result = await db.execute(enrollment_stmt)
    enrollment = result.scalar_one_or_none()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found in this organization"
        )
    return enrollment


async def _log_audit(
    db: AsyncSession,
    user_id: UUID,
    org_id: UUID,
    resource_type: str,
    resource_id: UUID,
    action: str,
    changes: dict = None
):
    """Create audit log entry for proxy operations."""
    log = AuditLog(
        actor_user_id=user_id,
        organization_id=org_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action_type=action,
        changes_json=changes,
    )
    db.add(log)


@router.get("", response_model=ProxyListResponse)
async def list_patient_proxies(
    org_id: UUID,
    patient_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db)
):
    """
    List all proxies assigned to a patient.
    """
    await _verify_patient_access(org_id, patient_id, db)
    
    # Query assignments with proxy and user info
    stmt = (
        select(PatientProxyAssignment, Proxy, User)
        .join(Proxy, PatientProxyAssignment.proxy_id == Proxy.id)
        .join(User, Proxy.user_id == User.id)
        .where(PatientProxyAssignment.patient_id == patient_id)
        .where(PatientProxyAssignment.revoked_at == None)
        .where(PatientProxyAssignment.deleted_at == None)
        .order_by(PatientProxyAssignment.granted_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    proxies = []
    for assignment, proxy, user in rows:
        proxies.append(ProxyAssignmentRead(
            id=assignment.id,
            proxy_id=proxy.id,
            patient_id=patient_id,
            relationship_type=assignment.relationship_type,
            can_view_profile=assignment.can_view_profile,
            can_view_appointments=assignment.can_view_appointments,
            can_schedule_appointments=assignment.can_schedule_appointments,
            can_view_clinical_notes=assignment.can_view_clinical_notes,
            can_view_billing=assignment.can_view_billing,
            can_message_providers=assignment.can_message_providers,
            granted_at=assignment.granted_at,
            expires_at=assignment.expires_at,
            revoked_at=assignment.revoked_at,
            user=ProxyUserInfo(
                id=user.id,
                email=user.email,
                display_name=user.display_name
            )
        ))
    
    return ProxyListResponse(patient_id=patient_id, proxies=proxies)


@router.post("", response_model=ProxyAssignmentRead, status_code=status.HTTP_201_CREATED)
async def assign_proxy(
    org_id: UUID,
    patient_id: UUID,
    data: ProxyAssignmentCreate,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign a proxy to a patient by email.
    If user exists, grants immediate access.
    """
    await _verify_patient_access(org_id, patient_id, db)
    now = datetime.now(timezone.utc)
    
    # Find user by email
    user_stmt = select(User).where(User.email == data.email).where(User.deleted_at == None)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email. User must have an account first."
        )
    
    # Find or create proxy profile for this user
    proxy_stmt = select(Proxy).where(Proxy.user_id == user.id).where(Proxy.deleted_at == None)
    proxy_result = await db.execute(proxy_stmt)
    proxy = proxy_result.scalar_one_or_none()
    
    if not proxy:
        proxy = Proxy(
            user_id=user.id,
            relationship_to_patient=data.relationship_type,
            created_at=now,
            updated_at=now
        )
        db.add(proxy)
        await db.flush()
    
    # Check if assignment already exists
    existing_stmt = (
        select(PatientProxyAssignment)
        .where(PatientProxyAssignment.proxy_id == proxy.id)
        .where(PatientProxyAssignment.patient_id == patient_id)
        .where(PatientProxyAssignment.revoked_at == None)
        .where(PatientProxyAssignment.deleted_at == None)
    )
    existing_result = await db.execute(existing_stmt)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already a proxy for this patient"
        )
    
    # Create assignment with permissions
    assignment = PatientProxyAssignment(
        proxy_id=proxy.id,
        patient_id=patient_id,
        relationship_type=data.relationship_type,
        can_view_profile=data.permissions.can_view_profile,
        can_view_appointments=data.permissions.can_view_appointments,
        can_schedule_appointments=data.permissions.can_schedule_appointments,
        can_view_clinical_notes=data.permissions.can_view_clinical_notes,
        can_view_billing=data.permissions.can_view_billing,
        can_message_providers=data.permissions.can_message_providers,
        granted_at=now,
        expires_at=data.expires_at,
        created_at=now,
        updated_at=now
    )
    db.add(assignment)
    
    # Audit log
    await _log_audit(
        db, member.user_id, org_id, "PROXY_ASSIGNMENT", assignment.id, "CREATE",
        {"proxy_email": data.email, "relationship": data.relationship_type}
    )
    
    await db.commit()
    await db.refresh(assignment)
    
    return ProxyAssignmentRead(
        id=assignment.id,
        proxy_id=proxy.id,
        patient_id=patient_id,
        relationship_type=assignment.relationship_type,
        can_view_profile=assignment.can_view_profile,
        can_view_appointments=assignment.can_view_appointments,
        can_schedule_appointments=assignment.can_schedule_appointments,
        can_view_clinical_notes=assignment.can_view_clinical_notes,
        can_view_billing=assignment.can_view_billing,
        can_message_providers=assignment.can_message_providers,
        granted_at=assignment.granted_at,
        expires_at=assignment.expires_at,
        revoked_at=assignment.revoked_at,
        user=ProxyUserInfo(
            id=user.id,
            email=user.email,
            display_name=user.display_name
        )
    )


@router.patch("/{assignment_id}", response_model=ProxyAssignmentRead)
async def update_proxy_permissions(
    org_id: UUID,
    patient_id: UUID,
    assignment_id: UUID,
    data: ProxyAssignmentUpdate,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Update proxy permissions.
    """
    await _verify_patient_access(org_id, patient_id, db)
    now = datetime.now(timezone.utc)
    
    # Get the assignment
    stmt = (
        select(PatientProxyAssignment, Proxy, User)
        .join(Proxy, PatientProxyAssignment.proxy_id == Proxy.id)
        .join(User, Proxy.user_id == User.id)
        .where(PatientProxyAssignment.id == assignment_id)
        .where(PatientProxyAssignment.patient_id == patient_id)
        .where(PatientProxyAssignment.revoked_at == None)
        .where(PatientProxyAssignment.deleted_at == None)
    )
    result = await db.execute(stmt)
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proxy assignment not found"
        )
    
    assignment, proxy, user = row
    
    changes = {}
    
    # Update permissions if provided
    if data.permissions:
        perms = data.permissions
        if perms.can_view_profile is not None:
            changes["can_view_profile"] = {"from": assignment.can_view_profile, "to": perms.can_view_profile}
            assignment.can_view_profile = perms.can_view_profile
        if perms.can_view_appointments is not None:
            changes["can_view_appointments"] = {"from": assignment.can_view_appointments, "to": perms.can_view_appointments}
            assignment.can_view_appointments = perms.can_view_appointments
        if perms.can_schedule_appointments is not None:
            changes["can_schedule_appointments"] = {"from": assignment.can_schedule_appointments, "to": perms.can_schedule_appointments}
            assignment.can_schedule_appointments = perms.can_schedule_appointments
        if perms.can_view_clinical_notes is not None:
            changes["can_view_clinical_notes"] = {"from": assignment.can_view_clinical_notes, "to": perms.can_view_clinical_notes}
            assignment.can_view_clinical_notes = perms.can_view_clinical_notes
        if perms.can_view_billing is not None:
            changes["can_view_billing"] = {"from": assignment.can_view_billing, "to": perms.can_view_billing}
            assignment.can_view_billing = perms.can_view_billing
        if perms.can_message_providers is not None:
            changes["can_message_providers"] = {"from": assignment.can_message_providers, "to": perms.can_message_providers}
            assignment.can_message_providers = perms.can_message_providers
    
    # Update expiration if provided
    if data.expires_at is not None:
        changes["expires_at"] = {"from": str(assignment.expires_at), "to": str(data.expires_at)}
        assignment.expires_at = data.expires_at
    
    assignment.updated_at = now
    
    # Audit log
    if changes:
        await _log_audit(
            db, member.user_id, org_id, "PROXY_ASSIGNMENT", assignment.id, "UPDATE",
            changes
        )
    
    await db.commit()
    await db.refresh(assignment)
    
    return ProxyAssignmentRead(
        id=assignment.id,
        proxy_id=proxy.id,
        patient_id=patient_id,
        relationship_type=assignment.relationship_type,
        can_view_profile=assignment.can_view_profile,
        can_view_appointments=assignment.can_view_appointments,
        can_schedule_appointments=assignment.can_schedule_appointments,
        can_view_clinical_notes=assignment.can_view_clinical_notes,
        can_view_billing=assignment.can_view_billing,
        can_message_providers=assignment.can_message_providers,
        granted_at=assignment.granted_at,
        expires_at=assignment.expires_at,
        revoked_at=assignment.revoked_at,
        user=ProxyUserInfo(
            id=user.id,
            email=user.email,
            display_name=user.display_name
        )
    )


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_proxy(
    org_id: UUID,
    patient_id: UUID,
    assignment_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke proxy access (soft delete with revoked_at).
    """
    await _verify_patient_access(org_id, patient_id, db)
    now = datetime.now(timezone.utc)
    
    # Get the assignment
    stmt = (
        select(PatientProxyAssignment)
        .where(PatientProxyAssignment.id == assignment_id)
        .where(PatientProxyAssignment.patient_id == patient_id)
        .where(PatientProxyAssignment.revoked_at == None)
        .where(PatientProxyAssignment.deleted_at == None)
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proxy assignment not found"
        )
    
    # Revoke access
    assignment.revoked_at = now
    assignment.updated_at = now
    
    # Audit log
    await _log_audit(
        db, member.user_id, org_id, "PROXY_ASSIGNMENT", assignment.id, "DELETE",
        {"revoked_at": str(now)}
    )
    
    await db.commit()
    return None

