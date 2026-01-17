import pytest
from sqlalchemy import select, text

from app.models.organization import Organization
from app.models.profile import Patient
from app.models.user import User


@pytest.mark.asyncio
async def test_tenant_isolation(db):
    # Setup: Create two organizations with unique IDs
    from ulid import ULID

    org1_id = str(ULID())
    org2_id = str(ULID())
    org1 = Organization(id=org1_id, name="Org 1", slug=f"org1_{org1_id}")
    org2 = Organization(id=org2_id, name="Org 2", slug=f"org2_{org2_id}")
    db.add_all([org1, org2])
    await db.flush()

    # Create two users
    u1_id = str(ULID())
    u2_id = str(ULID())
    u1 = User(id=u1_id, email=f"u1_{u1_id}@test.com")
    u2 = User(id=u2_id, email=f"u2_{u2_id}@test.com")
    db.add_all([u1, u2])
    await db.flush()

    # Create a patient in Org 1
    p1_id = str(ULID())
    p1 = Patient(
        id=p1_id,
        user_id=u1.id,
        organization_id=org1.id,
        mrn=f"MRN1_{p1_id}",
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

    # Debug: check current role and tenant
    res = await db.execute(
        text("SELECT current_user, current_setting('app.current_tenant_id', true)")
    )
    debug_info = res.fetchone()
    print(f"\nDEBUG: role={debug_info[0]}, tenant={debug_info[1]}")

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
    assert patients[0].mrn == f"MRN1_{p1_id}"

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
