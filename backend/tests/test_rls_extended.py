from datetime import UTC, datetime

import pytest
from sqlalchemy import select, text

from app.models.appointment import Appointment
from app.models.organization import Organization
from app.models.profile import Patient
from app.models.user import User


@pytest.mark.asyncio
async def test_appointment_rls(db):
    # Setup: Create two organizations
    org1 = Organization(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6O1", name="Org 1", slug="org1")
    org2 = Organization(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6O2", name="Org 2", slug="org2")
    db.add_all([org1, org2])
    await db.flush()

    # Create users
    u1 = User(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6U1", email="u1@test.com")
    db.add(u1)
    await db.flush()

    # Create a patient in Org 1
    p1 = Patient(
        id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6P1",
        user_id=u1.id,
        organization_id=org1.id,
        mrn="MRN1",
        first_name="RLS",
        last_name="Test",
    )
    db.add(p1)
    await db.flush()

    # Create an appointment in Org 1
    appt1 = Appointment(
        id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6A1",
        organization_id=org1.id,
        patient_id=p1.id,
        scheduled_at=datetime.now(UTC),
        status="SCHEDULED",
    )
    db.add(appt1)
    await db.flush()

    # Create test user for RLS
    await db.execute(text("DROP ROLE IF EXISTS rls_test_user"))
    await db.execute(text("CREATE ROLE rls_test_user WITH LOGIN"))
    await db.execute(
        text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rls_test_user")
    )
    await db.execute(
        text("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rls_test_user")
    )

    await db.execute(text("SET ROLE rls_test_user"))

    # Switch to Org 2
    await db.execute(
        text(f"SELECT set_config('app.current_tenant_id', '{org2.id}', true)")
    )

    # Try to query appointments
    stmt = select(Appointment)
    result = await db.execute(stmt)
    appointments = result.scalars().all()

    # Should be empty because appt1 is in org_1
    # This assertion will FAIL if RLS is not enabled
    assert len(appointments) == 0

    # Switch to Org 1
    await db.execute(
        text(f"SELECT set_config('app.current_tenant_id', '{org1.id}', true)")
    )
    result = await db.execute(stmt)
    appointments = result.scalars().all()
    assert len(appointments) == 1
    assert appointments[0].id == appt1.id

    # Cleanup
    await db.execute(text("RESET ROLE"))
    await db.execute(
        text("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM rls_test_user")
    )
    await db.execute(
        text(
            "REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM rls_test_user"
        )
    )
    await db.execute(text("DROP ROLE rls_test_user"))
