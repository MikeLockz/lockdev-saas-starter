from datetime import date

import pytest
from sqlalchemy import select

from src.models import Patient, User


@pytest.mark.asyncio
async def test_create_user_and_patient(db_session):
    import uuid

    email = f"test_patient_{uuid.uuid4()}@example.com"
    # Create User
    user = User(email=email, password_hash="hash")
    db_session.add(user)
    await db_session.flush()  # Get ID

    assert user.id is not None

    # Create Patient
    patient = Patient(user_id=user.id, first_name="John", last_name="Doe", dob=date(2000, 1, 1))
    db_session.add(patient)
    await db_session.commit()

    # Verify
    stmt = select(User).where(User.email == email)
    result = await db_session.execute(stmt)
    fetched_user = result.scalar_one()

    stmt_p = select(Patient).where(Patient.user_id == fetched_user.id)
    result_p = await db_session.execute(stmt_p)
    fetched_patient = result_p.scalar_one()
    assert fetched_patient.first_name == "John"
