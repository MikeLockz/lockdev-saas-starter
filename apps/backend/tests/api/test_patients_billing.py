import uuid
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.profiles import Patient
from src.models.users import User


@pytest.fixture
async def db(db_session):
    return db_session


@pytest.fixture
async def patient_user(db: AsyncSession):
    user = User(email=f"patient_{uuid.uuid4()}@example.com", password_hash="hash", display_name="Patient User")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def patient_user_auth_headers(patient_user):
    return {"Authorization": f"Bearer mock_{patient_user.email}"}


@pytest.fixture
async def patient(db: AsyncSession, patient_user):
    patient = Patient(
        user_id=patient_user.id,
        first_name="John",
        last_name="Doe",
        dob=date(1990, 1, 1),
        subscription_status="NONE",
        billing_manager_id=None,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@pytest.fixture
async def other_user(db: AsyncSession):
    user = User(email=f"other_{uuid.uuid4()}@example.com", password_hash="hash", display_name="Other User")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def other_user_auth_headers(other_user):
    return {"Authorization": f"Bearer mock_{other_user.email}"}


@pytest.mark.asyncio
async def test_patient_billing_access_denied_for_other_user(
    client: AsyncClient, patient_user: User, other_user: User, patient: Patient, other_user_auth_headers: dict
):
    """Test that a user cannot access another patient's billing."""
    response = await client.get(f"/api/v1/patients/{patient.id}/billing/subscription", headers=other_user_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_patient_billing_access_allowed_for_owner(
    client: AsyncClient, patient_user: User, patient: Patient, patient_user_auth_headers: dict
):
    """Test that patient can access their own billing."""
    response = await client.get(
        f"/api/v1/patients/{patient.id}/billing/subscription", headers=patient_user_auth_headers
    )
    # 200 explicitly returns status="NONE"
    assert response.status_code == 200
    assert response.json()["status"] == "NONE"
