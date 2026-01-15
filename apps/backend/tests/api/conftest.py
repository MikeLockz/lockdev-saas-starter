from datetime import UTC

import pytest

from src.models import Organization, OrganizationMember


@pytest.fixture
async def test_org(db_session, test_user):
    import uuid
    from datetime import datetime

    now = datetime.now(UTC)
    org = Organization(
        name=f"Test Org {uuid.uuid4()}",
        tax_id=f"12-{uuid.uuid4()}"[:10],  # Random tax id
        created_at=now,
        updated_at=now,
        member_count=1,
    )
    db_session.add(org)
    await db_session.flush()  # get id

    member = OrganizationMember(
        organization_id=org.id, user_id=test_user.id, role="ADMIN", created_at=now, updated_at=now
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(org)

    yield org

    await db_session.delete(member)
    await db_session.delete(org)
    await db_session.commit()
