from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models.contacts import ContactMethod
from src.models.organizations import OrganizationMember, OrganizationPatient
from src.models.profiles import Patient
from src.models.users import User
from src.schemas.patients import (
    ContactMethodRead,
    PaginatedPatients,
    PatientCreate,
    PatientListItem,
    PatientRead,
    PatientUpdate,
)
from src.security.auth import get_current_user
from src.security.mfa import require_mfa
from src.security.org_access import get_current_org_member

router = APIRouter()


async def _get_accessible_patient_ids(
    db: AsyncSession,
    user: User,
    member: OrganizationMember,
    org_id: UUID,
) -> list[UUID] | None:
    """
    Get list of patient IDs the user can access based on their role.
    Returns None if user can access all patients (Staff/Admin/Provider).
    Returns list of patient IDs for Patient/Proxy roles.
    """
    # Staff, Admin, Provider can see all patients
    if member.role in ("STAFF", "ADMIN", "PROVIDER"):
        return None

    accessible_ids = []

    # Check if user is a patient - they can see themselves
    patient_stmt = select(Patient.id).where(Patient.user_id == user.id).where(Patient.deleted_at.is_(None))
    patient_result = await db.execute(patient_stmt)
    own_patient_id = patient_result.scalar_one_or_none()
    if own_patient_id:
        accessible_ids.append(own_patient_id)

    # Check if user is a proxy - they can see assigned patients
    from src.models.assignments import PatientProxyAssignment
    from src.models.profiles import Proxy

    proxy_stmt = select(Proxy).where(Proxy.user_id == user.id).where(Proxy.deleted_at.is_(None))
    proxy_result = await db.execute(proxy_stmt)
    proxy = proxy_result.scalar_one_or_none()

    if proxy:
        now = datetime.now(UTC)
        assignment_stmt = (
            select(PatientProxyAssignment.patient_id)
            .where(PatientProxyAssignment.proxy_id == proxy.id)
            .where(PatientProxyAssignment.revoked_at.is_(None))
            .where(PatientProxyAssignment.deleted_at.is_(None))
            .where((PatientProxyAssignment.expires_at.is_(None)) | (PatientProxyAssignment.expires_at > now))
        )
        assignment_result = await db.execute(assignment_stmt)
        proxy_patient_ids = assignment_result.scalars().all()
        accessible_ids.extend(proxy_patient_ids)

    return accessible_ids


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
    org_id: UUID,
    patient_data: PatientCreate,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new patient and enroll in the organization.
    """
    now = datetime.now(UTC)

    # Create Patient
    patient = Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        dob=patient_data.dob,
        legal_sex=patient_data.legal_sex,
        medical_record_number=patient_data.medical_record_number,
        created_at=now,
        updated_at=now,
    )
    db.add(patient)
    await db.flush()  # Get patient ID

    # Create OrganizationPatient enrollment
    enrollment = OrganizationPatient(organization_id=org_id, patient_id=patient.id, status="ACTIVE", enrolled_at=now)
    db.add(enrollment)

    # Create contact methods if provided
    if patient_data.contact_methods:
        for cm_data in patient_data.contact_methods:
            contact = ContactMethod(
                patient_id=patient.id,
                type=cm_data.type,
                value=cm_data.value,
                is_primary=cm_data.is_primary,
                is_safe_for_voicemail=cm_data.is_safe_for_voicemail,
                label=cm_data.label,
                created_at=now,
                updated_at=now,
            )
            db.add(contact)

    await db.commit()

    # Reload with relationships
    stmt = select(Patient).options(selectinload(Patient.contact_methods)).where(Patient.id == patient.id)
    result = await db.execute(stmt)
    patient = result.scalar_one()

    # Build response with enrollment info
    return PatientRead(
        id=patient.id,
        user_id=patient.user_id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        dob=patient.dob,
        legal_sex=patient.legal_sex,
        medical_record_number=patient.medical_record_number,
        stripe_customer_id=patient.stripe_customer_id,
        subscription_status=patient.subscription_status,
        contact_methods=[ContactMethodRead.model_validate(cm) for cm in patient.contact_methods],
        enrolled_at=enrollment.enrolled_at,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


@router.get("", response_model=PaginatedPatients)
async def list_patients(
    org_id: UUID,
    name: str | None = Query(None, description="Fuzzy search by name"),
    mrn: str | None = Query(None, description="Search by MRN"),
    status_filter: str | None = Query(None, alias="status", description="ACTIVE or DISCHARGED"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    List patients enrolled in the organization with optional filters.
    Role-based access control:
    - Staff/Admin/Provider: see all patients
    - Patient: see only themselves
    - Proxy: see only assigned patients
    """
    # Get accessible patient IDs based on role
    accessible_ids = await _get_accessible_patient_ids(db, current_user, member, org_id)

    # If role restricts access and no accessible patients, return empty
    if accessible_ids is not None and len(accessible_ids) == 0:
        return PaginatedPatients(items=[], total=0, limit=limit, offset=offset)

    # Base query: patients enrolled in this org
    base_query = (
        select(Patient, OrganizationPatient)
        .join(OrganizationPatient, Patient.id == OrganizationPatient.patient_id)
        .where(OrganizationPatient.organization_id == org_id)
        .where(Patient.deleted_at.is_(None))
    )

    # Apply role-based filter if restricted
    if accessible_ids is not None:
        base_query = base_query.where(Patient.id.in_(accessible_ids))

    # Apply filters
    if status_filter:
        base_query = base_query.where(OrganizationPatient.status == status_filter.upper())
    else:
        # Default to active
        base_query = base_query.where(OrganizationPatient.status == "ACTIVE")

    if name:
        # Trigram fuzzy search on first_name or last_name
        search_pattern = f"%{name}%"
        base_query = base_query.where(
            or_(Patient.first_name.ilike(search_pattern), Patient.last_name.ilike(search_pattern))
        )

    if mrn:
        base_query = base_query.where(Patient.medical_record_number.ilike(f"%{mrn}%"))

    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    paginated_query = base_query.order_by(Patient.last_name, Patient.first_name).offset(offset).limit(limit)
    result = await db.execute(paginated_query)
    rows = result.all()

    items = []
    for patient, enrollment in rows:
        items.append(
            PatientListItem(
                id=patient.id,
                first_name=patient.first_name,
                last_name=patient.last_name,
                dob=patient.dob,
                medical_record_number=patient.medical_record_number,
                enrolled_at=enrollment.enrolled_at,
                status=enrollment.status,
            )
        )

    return PaginatedPatients(items=items, total=total, limit=limit, offset=offset)


@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(
    org_id: UUID,
    patient_id: UUID,
    request: Request,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Get full patient details with contact methods.
    """
    # Verify patient is in organization
    enrollment_stmt = (
        select(OrganizationPatient)
        .where(OrganizationPatient.organization_id == org_id)
        .where(OrganizationPatient.patient_id == patient_id)
    )
    enrollment_result = await db.execute(enrollment_stmt)
    enrollment = enrollment_result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found in this organization")

    # Get patient with contact methods
    stmt = (
        select(Patient)
        .options(selectinload(Patient.contact_methods))
        .where(Patient.id == patient_id)
        .where(Patient.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # HIPAA: Audit log for PHI access
    from src.models.audit import AuditLog

    audit = AuditLog(
        actor_user_id=member.user_id,
        organization_id=org_id,
        resource_type="PATIENT",
        resource_id=patient_id,
        action_type="READ",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(audit)
    await db.commit()

    return PatientRead(
        id=patient.id,
        user_id=patient.user_id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        dob=patient.dob,
        legal_sex=patient.legal_sex,
        medical_record_number=patient.medical_record_number,
        stripe_customer_id=patient.stripe_customer_id,
        subscription_status=patient.subscription_status,
        contact_methods=[ContactMethodRead.model_validate(cm) for cm in patient.contact_methods],
        enrolled_at=enrollment.enrolled_at,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


@router.patch("/{patient_id}", response_model=PatientRead)
async def update_patient(
    org_id: UUID,
    patient_id: UUID,
    patient_update: PatientUpdate,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Update patient fields. Requires org membership.
    """
    # Verify patient is in organization
    enrollment_stmt = (
        select(OrganizationPatient)
        .where(OrganizationPatient.organization_id == org_id)
        .where(OrganizationPatient.patient_id == patient_id)
    )
    enrollment_result = await db.execute(enrollment_stmt)
    enrollment = enrollment_result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found in this organization")

    # Get patient
    stmt = (
        select(Patient)
        .options(selectinload(Patient.contact_methods))
        .where(Patient.id == patient_id)
        .where(Patient.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Apply updates
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    patient.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(patient)

    return PatientRead(
        id=patient.id,
        user_id=patient.user_id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        dob=patient.dob,
        legal_sex=patient.legal_sex,
        medical_record_number=patient.medical_record_number,
        stripe_customer_id=patient.stripe_customer_id,
        subscription_status=patient.subscription_status,
        contact_methods=[ContactMethodRead.model_validate(cm) for cm in patient.contact_methods],
        enrolled_at=enrollment.enrolled_at,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def discharge_patient(
    org_id: UUID,
    patient_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Discharge a patient from the organization (soft delete via status change).
    """
    # Update OrganizationPatient status
    enrollment_stmt = (
        select(OrganizationPatient)
        .where(OrganizationPatient.organization_id == org_id)
        .where(OrganizationPatient.patient_id == patient_id)
    )
    enrollment_result = await db.execute(enrollment_stmt)
    enrollment = enrollment_result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found in this organization")

    enrollment.status = "DISCHARGED"
    enrollment.discharged_at = datetime.now(UTC)

    await db.commit()
    return None


# ========================
# CONTACT METHODS ENDPOINTS
# ========================


from src.schemas.patients import ContactMethodCreate


class ContactMethodUpdate(ContactMethodCreate):
    """Partial update for contact method."""

    type: str | None = None
    value: str | None = None
    is_primary: bool | None = None
    is_safe_for_voicemail: bool | None = None
    label: str | None = None


async def _verify_patient_access(org_id: UUID, patient_id: UUID, db: AsyncSession) -> OrganizationPatient:
    """Helper to verify patient is in organization."""
    enrollment_stmt = (
        select(OrganizationPatient)
        .where(OrganizationPatient.organization_id == org_id)
        .where(OrganizationPatient.patient_id == patient_id)
    )
    enrollment_result = await db.execute(enrollment_stmt)
    enrollment = enrollment_result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found in this organization")
    return enrollment


@router.get("/{patient_id}/contact-methods", response_model=list[ContactMethodRead])
async def list_contact_methods(
    org_id: UUID,
    patient_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    List all contact methods for a patient.
    """
    await _verify_patient_access(org_id, patient_id, db)

    stmt = (
        select(ContactMethod)
        .where(ContactMethod.patient_id == patient_id)
        .order_by(ContactMethod.is_primary.desc(), ContactMethod.type)
    )
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    return [ContactMethodRead.model_validate(c) for c in contacts]


@router.post("/{patient_id}/contact-methods", response_model=ContactMethodRead, status_code=status.HTTP_201_CREATED)
async def create_contact_method(
    org_id: UUID,
    patient_id: UUID,
    contact_data: ContactMethodCreate,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new contact method to a patient.
    If is_primary=True, unsets other primaries of the same type.
    """
    await _verify_patient_access(org_id, patient_id, db)
    now = datetime.now(UTC)

    # If setting as primary, unset existing primaries of same type
    if contact_data.is_primary:
        update_stmt = (
            select(ContactMethod)
            .where(ContactMethod.patient_id == patient_id)
            .where(ContactMethod.type == contact_data.type)
            .where(ContactMethod.is_primary)
        )
        result = await db.execute(update_stmt)
        existing_primaries = result.scalars().all()
        for existing in existing_primaries:
            existing.is_primary = False
            existing.updated_at = now

    contact = ContactMethod(
        patient_id=patient_id,
        type=contact_data.type,
        value=contact_data.value,
        is_primary=contact_data.is_primary,
        is_safe_for_voicemail=contact_data.is_safe_for_voicemail,
        label=contact_data.label,
        created_at=now,
        updated_at=now,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    return ContactMethodRead.model_validate(contact)


@router.patch("/{patient_id}/contact-methods/{contact_id}", response_model=ContactMethodRead)
async def update_contact_method(
    org_id: UUID,
    patient_id: UUID,
    contact_id: UUID,
    contact_update: ContactMethodUpdate,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a contact method.
    If is_primary becomes True, unsets other primaries of the same type.
    """
    await _verify_patient_access(org_id, patient_id, db)
    now = datetime.now(UTC)

    # Get the contact
    stmt = select(ContactMethod).where(ContactMethod.id == contact_id).where(ContactMethod.patient_id == patient_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact method not found")

    update_data = contact_update.model_dump(exclude_unset=True)

    # Handle primary switching
    if update_data.get("is_primary") is True and not contact.is_primary:
        contact_type = update_data.get("type", contact.type)
        update_primaries_stmt = (
            select(ContactMethod)
            .where(ContactMethod.patient_id == patient_id)
            .where(ContactMethod.type == contact_type)
            .where(ContactMethod.is_primary)
            .where(ContactMethod.id != contact_id)
        )
        existing_result = await db.execute(update_primaries_stmt)
        for existing in existing_result.scalars().all():
            existing.is_primary = False
            existing.updated_at = now

    # Apply updates
    for field, value in update_data.items():
        setattr(contact, field, value)

    contact.updated_at = now

    await db.commit()
    await db.refresh(contact)

    return ContactMethodRead.model_validate(contact)


@router.delete("/{patient_id}/contact-methods/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_method(
    org_id: UUID,
    patient_id: UUID,
    contact_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a contact method.
    Cannot delete the only primary contact of any type.
    """
    await _verify_patient_access(org_id, patient_id, db)

    # Get the contact to delete
    stmt = select(ContactMethod).where(ContactMethod.id == contact_id).where(ContactMethod.patient_id == patient_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact method not found")

    # Check if this is the only primary of its type
    if contact.is_primary:
        count_stmt = (
            select(func.count())
            .select_from(ContactMethod)
            .where(ContactMethod.patient_id == patient_id)
            .where(ContactMethod.type == contact.type)
        )
        count_result = await db.execute(count_stmt)
        total_of_type = count_result.scalar() or 0

        if total_of_type <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete the only {contact.type} contact. Add another one first.",
            )

    await db.delete(contact)
    await db.commit()
    return None


# ========================
# CARE TEAM ENDPOINTS
# ========================

from src.models.care_teams import CareTeamAssignment
from src.models.profiles import Provider
from src.schemas.care_teams import (
    CareTeamAssignmentCreate,
    CareTeamAssignmentRead,
    CareTeamList,
    CareTeamMember,
    CareTeamProviderInfo,
)


@router.get("/{patient_id}/care-team", response_model=CareTeamList)
async def get_care_team(
    org_id: UUID,
    patient_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all providers assigned to a patient's care team.
    """
    await _verify_patient_access(org_id, patient_id, db)

    # Query care team assignments with provider and user info
    stmt = (
        select(CareTeamAssignment, Provider, User)
        .join(Provider, CareTeamAssignment.provider_id == Provider.id)
        .join(User, Provider.user_id == User.id)
        .where(CareTeamAssignment.patient_id == patient_id)
        .where(CareTeamAssignment.organization_id == org_id)
        .where(CareTeamAssignment.removed_at.is_(None))
        .order_by(
            # PRIMARY first, then by assigned_at
            CareTeamAssignment.role.desc(),
            CareTeamAssignment.assigned_at,
        )
    )
    result = await db.execute(stmt)
    rows = result.all()

    members = []
    primary_provider = None

    for assignment, provider, user in rows:
        team_member = CareTeamMember(
            assignment_id=assignment.id,
            provider_id=provider.id,
            role=assignment.role,
            assigned_at=assignment.assigned_at,
            provider_name=user.display_name or user.email,
            provider_specialty=provider.specialty,
            provider_npi=provider.npi_number,
        )
        members.append(team_member)

        if assignment.role == "PRIMARY":
            primary_provider = team_member

    return CareTeamList(patient_id=patient_id, members=members, primary_provider=primary_provider)


@router.post("/{patient_id}/care-team", response_model=CareTeamAssignmentRead, status_code=status.HTTP_201_CREATED)
async def assign_to_care_team(
    org_id: UUID,
    patient_id: UUID,
    assignment_data: CareTeamAssignmentCreate,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Assign a provider to a patient's care team.
    Only one PRIMARY provider allowed per patient.
    """
    await _verify_patient_access(org_id, patient_id, db)
    now = datetime.now(UTC)

    # Normalize role
    role = assignment_data.role.upper()
    valid_roles = {"PRIMARY", "SPECIALIST", "CONSULTANT"}
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    # Verify provider exists and belongs to this organization
    provider_stmt = (
        select(Provider)
        .where(Provider.id == assignment_data.provider_id)
        .where(Provider.organization_id == org_id)
        .where(Provider.deleted_at.is_(None))
        .where(Provider.is_active)
    )
    provider_result = await db.execute(provider_stmt)
    provider = provider_result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found in this organization")

    # Check if already assigned
    existing_stmt = (
        select(CareTeamAssignment)
        .where(CareTeamAssignment.patient_id == patient_id)
        .where(CareTeamAssignment.provider_id == assignment_data.provider_id)
        .where(CareTeamAssignment.removed_at.is_(None))
    )
    existing_result = await db.execute(existing_stmt)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This provider is already assigned to this patient's care team"
        )

    # Check PRIMARY constraint: only one PRIMARY per patient
    if role == "PRIMARY":
        primary_stmt = (
            select(CareTeamAssignment)
            .where(CareTeamAssignment.patient_id == patient_id)
            .where(CareTeamAssignment.organization_id == org_id)
            .where(CareTeamAssignment.role == "PRIMARY")
            .where(CareTeamAssignment.removed_at.is_(None))
        )
        primary_result = await db.execute(primary_stmt)
        existing_primary = primary_result.scalar_one_or_none()

        if existing_primary:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient already has a PRIMARY provider. Remove the existing PRIMARY first or assign as SPECIALIST/CONSULTANT.",
            )

    # Create assignment
    assignment = CareTeamAssignment(
        organization_id=org_id,
        patient_id=patient_id,
        provider_id=assignment_data.provider_id,
        role=role,
        assigned_at=now,
        created_at=now,
        updated_at=now,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    # Get user for response
    user_stmt = select(User).where(User.id == provider.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one()

    return CareTeamAssignmentRead(
        id=assignment.id,
        patient_id=assignment.patient_id,
        provider_id=assignment.provider_id,
        role=assignment.role,
        assigned_at=assignment.assigned_at,
        removed_at=assignment.removed_at,
        provider=CareTeamProviderInfo(
            id=provider.id,
            user_id=provider.user_id,
            npi_number=provider.npi_number,
            specialty=provider.specialty,
            user_display_name=user.display_name,
            user_email=user.email,
        ),
    )


@router.delete("/{patient_id}/care-team/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_care_team(
    org_id: UUID,
    patient_id: UUID,
    assignment_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    _mfa_user: User = Depends(require_mfa),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a provider from a patient's care team (soft delete).
    """
    await _verify_patient_access(org_id, patient_id, db)
    now = datetime.now(UTC)

    # Get the assignment
    stmt = (
        select(CareTeamAssignment)
        .where(CareTeamAssignment.id == assignment_id)
        .where(CareTeamAssignment.patient_id == patient_id)
        .where(CareTeamAssignment.organization_id == org_id)
        .where(CareTeamAssignment.removed_at.is_(None))
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Care team assignment not found")

    # Soft delete by setting removed_at
    assignment.removed_at = now
    assignment.updated_at = now

    await db.commit()
    return None
