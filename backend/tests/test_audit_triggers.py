import pytest
from sqlalchemy import text

from app.models.organization import Organization


@pytest.mark.asyncio
async def test_audit_trigger_works(db):
    # Setup: Ensure we are using a fresh engine/session that can commit for real
    # (or just use the existing db fixture if it handles commits)

    org = Organization(
        id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6O3", name="Audit Org", slug="audit-org"
    )
    db.add(org)
    await db.commit()

    # Check activity table (postgresql-audit)
    # We use text() because activity is managed by postgresql-audit and not necessarily in our models
    result = await db.execute(
        text("SELECT count(*) FROM activity WHERE table_name = 'organizations'")
    )
    count = result.scalar()
    assert count >= 1
