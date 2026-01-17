from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from ulid import ULID

from app.models.appointment import Appointment
from app.models.organization import Organization
from app.models.profile import Patient
from app.models.user import User


@pytest.mark.asyncio
async def test_audit_trigger_works(db):
    # Setup: Ensure we are using a fresh engine/session that can commit for real
    # (or just use the existing db fixture if it handles commits)

    org_id = str(ULID())
    org = Organization(
        id=org_id, name="Audit Org " + org_id, slug="audit-org-" + org_id
    )
    db.add(org)
    await db.commit()

    # Check activity table (postgresql-audit uses text() for raw queries)
    # We filter by row_data ->> 'id' because count(*) might match other tests
    stmt = text(
        "SELECT count(*) FROM activity "
        "WHERE table_name = 'organizations' "
        "AND changed_data->>'id' = :id"
    ).bindparams(id=org_id)
    result = await db.execute(stmt)
    count = result.scalar()
    assert count == 1, "Organization audit log missing"

    # Test Appointment (New Table)
    user_id = str(ULID())
    u = User(id=user_id, email=f"u_{user_id}@test.com")
    db.add(u)

    patient_id = str(ULID())
    p = Patient(
        id=patient_id,
        user_id=user_id,
        organization_id=org_id,
        mrn="M" + patient_id,
        first_name="A",
        last_name="T",
    )
    db.add(p)

    appt_id = str(ULID())
    appt = Appointment(
        id=appt_id,
        organization_id=org_id,
        patient_id=patient_id,
        scheduled_at=datetime.now(UTC),
        status="SCHEDULED",
    )
    db.add(appt)
    await db.commit()

    stmt = text(
        "SELECT count(*) FROM activity "
        "WHERE table_name = 'appointments' "
        "AND changed_data->>'id' = :id"
    ).bindparams(id=appt_id)
    result = await db.execute(stmt)
    count = result.scalar()
    assert count == 1, "Appointment audit log missing"
