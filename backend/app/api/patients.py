from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.org_access import get_current_org_member
from app.models.contact import ContactMethod
from app.models.profile import Patient
from app.models.user import User
from app.schemas.contacts import ContactMethodCreate, ContactMethodRead
from app.schemas.patients import PatientCreate, PatientRead, PatientUpdate

router = APIRouter()


@router.post(
    "/{org_id}/patients",
    response_model=PatientRead,
    summary="Create Patient",
    description="Registers a new patient within the specified organization.",
)
async def create_patient(
    org_id: str,
    req: PatientCreate,
    _member: User = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new patient in the organization.
    """
    patient = Patient(
        organization_id=org_id,
        first_name=req.first_name,
        last_name=req.last_name,
        mrn=req.mrn,
        dob=req.dob,
        gender=req.gender,
        preferred_language=req.preferred_language,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get(
    "/{org_id}/patients",
    response_model=list[PatientRead],
    summary="List Patients",
    description="Retrieves a paginated list of patients in the organization.",
)
async def list_patients(
    org_id: str,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
    _member: User = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    List patients in the organization with optional search and pagination.
    """
    stmt = (
        select(Patient)
        .where(Patient.organization_id == org_id)
        .options(selectinload(Patient.contact_methods))
    )

    if search:
        stmt = stmt.where(
            or_(
                Patient.first_name.ilike(f"%{search}%"),
                Patient.last_name.ilike(f"%{search}%"),
                Patient.mrn.ilike(f"%{search}%"),
            )
        )

    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/{org_id}/patients/{patient_id}",
    response_model=PatientRead,
    summary="Get patient details",
    description=(
        "Retrieves full profile details for a specific patient, including "
        "contact methods."
    ),
)
async def get_patient(
    org_id: str,
    patient_id: str,
    _member: User = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific patient.
    """
    stmt = (
        select(Patient)
        .where(Patient.id == patient_id, Patient.organization_id == org_id)
        .options(selectinload(Patient.contact_methods))
    )
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch(
    "/{org_id}/patients/{patient_id}",
    response_model=PatientRead,
    summary="Update patient",
    description="Updates information for an existing patient record.",
)
async def update_patient(
    org_id: str,
    patient_id: str,
    req: PatientUpdate,
    _member: User = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    Update patient details.
    """
    stmt = (
        select(Patient)
        .where(Patient.id == patient_id, Patient.organization_id == org_id)
        .options(selectinload(Patient.contact_methods))
    )
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)

    await db.commit()
    await db.refresh(patient)
    return patient


@router.get(
    "/{org_id}/patients/{patient_id}/contact-methods",
    response_model=list[ContactMethodRead],
    summary="List contact methods",
    description=(
        "Retrieves all contact methods (phone, email, SMS) associated with "
        "a patient."
    ),
)
async def list_contact_methods(
    org_id: str,
    patient_id: str,
    _member: User = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    List all contact methods for a patient.
    """
    patient = await db.get(Patient, patient_id)
    if not patient or patient.organization_id != org_id:
        raise HTTPException(status_code=404, detail="Patient not found")

    stmt = select(ContactMethod).where(ContactMethod.patient_id == patient_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/{org_id}/patients/{patient_id}/contact-methods",
    response_model=ContactMethodRead,
    summary="Add contact method",
    description=(
        "Adds a new contact method to a patient profile. If set as primary, "
        "other methods of the same type will be demoted."
    ),
)
async def create_contact_method(
    org_id: str,
    patient_id: str,
    req: ContactMethodCreate,
    _member: User = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new contact method for a patient.
    """
    patient = await db.get(Patient, patient_id)
    if not patient or patient.organization_id != org_id:
        raise HTTPException(status_code=404, detail="Patient not found")

    async with db.begin():
        if req.is_primary:
            # Unset other primaries of same type
            stmt = (
                update(ContactMethod)
                .where(
                    ContactMethod.patient_id == patient_id,
                    ContactMethod.type == req.type,
                )
                .values(is_primary=False)
            )
            await db.execute(stmt)

        contact = ContactMethod(
            patient_id=patient_id,
            type=req.type,
            value=req.value,
            label=req.label,
            is_primary=req.is_primary,
            is_safe_for_voicemail=req.is_safe_for_voicemail,
        )
        db.add(contact)

    await db.refresh(contact)
    return contact
