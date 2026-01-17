import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.organization import Organization
from app.models.profile import Patient
from app.models.user import User


@pytest.mark.asyncio
async def test_create_user_with_patient(client, db):
    # Setup Org
    org = Organization(id="org_test_1", name="Test Org", slug="test-org-1")
    db.add(org)
    await db.flush()

    # Create User
    user = User(email="test-user@example.com")
    db.add(user)
    await db.flush()

    # Create Patient Profile
    patient = Patient(
        user_id=user.id,
        organization_id=org.id,
        first_name="Test",
        last_name="User",
        mrn="MRN-TEST-1",
    )
    db.add(patient)
    await db.flush()

    # Reload with profile
    stmt = (
        select(User)
        .where(User.id == user.id)
        .options(selectinload(User.patient_profile))
    )
    result = await db.execute(stmt)
    user = result.scalar_one()

    assert patient.user_id == user.id
    assert user.patient_profile.mrn == "MRN-TEST-1"


@pytest.mark.asyncio
async def test_soft_delete_patient(db):
    # Setup Org
    org = Organization(id="org_test_2", name="Test Org 2", slug="test-org-2")
    db.add(org)
    await db.flush()

    user = User(email="test-delete-2@example.com")
    db.add(user)
    await db.flush()

    patient = Patient(
        user_id=user.id,
        organization_id=org.id,
        first_name="Delete",
        last_name="Me",
        mrn="MRN-DEL-2",
    )
    db.add(patient)
    await db.flush()

    # Manually set deleted_at
    import datetime

    patient.deleted_at = datetime.datetime.now(datetime.UTC)
    await db.flush()

    # Verify it's still in DB but has deleted_at set
    stmt = select(Patient).where(Patient.mrn == "MRN-DEL-2")
    result = await db.execute(stmt)
    p = result.scalar_one()
    assert p.deleted_at is not None
