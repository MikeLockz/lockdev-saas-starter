import pytest
from sqlalchemy import select, text

from app.models.organization import Organization
from app.models.profile import Patient
from app.models.user import User


@pytest.mark.asyncio
async def test_tenant_isolation(db):
    # Setup: Create two organizations
    org1 = Organization(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6O1", name="Org 1", slug="org1")
    org2 = Organization(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6O2", name="Org 2", slug="org2")
    db.add_all([org1, org2])
    await db.flush()

    # Create two users
    u1 = User(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6U1", email="u1@test.com")
    u2 = User(id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6U2", email="u2@test.com")
    db.add_all([u1, u2])
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

    # Set session context to Org 2
    # To test RLS, we need a user that is NOT a superuser and doesn't have BYPASSRLS.
    await db.execute(text("DROP ROLE IF EXISTS rls_test_user"))
    await db.execute(text("CREATE ROLE rls_test_user WITH LOGIN"))
    await db.execute(
        text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rls_test_user")
    )
    await db.execute(
        text("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rls_test_user")
    )

    await db.execute(text("SET ROLE rls_test_user"))

    await db.execute(
        text(f"SELECT set_config('app.current_tenant_id', '{org2.id}', true)")
    )

    # Try to query patients
    stmt = select(Patient)
    result = await db.execute(stmt)
    patients = result.scalars().all()

    # Should be empty because p1 is in org_1
    assert len(patients) == 0

    # Set session context to Org 1
    await db.execute(
        text(f"SELECT set_config('app.current_tenant_id', '{org1.id}', true)")
    )
    result = await db.execute(stmt)
    patients = result.scalars().all()
    assert len(patients) == 1
    assert patients[0].mrn == "MRN1"

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
