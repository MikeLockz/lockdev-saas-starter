import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.main import app
from app.models.organization import Organization
from app.models.user import User


@pytest.mark.asyncio
async def test_list_organizations(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"user_{uid}@test.com", is_superuser=True)
    db.add(user)
    org_id = str(ULID())
    org = Organization(id=org_id, name="List Org", slug=f"list-org-{org_id}")
    db.add(org)
    from app.models.organization import OrganizationMember

    member = OrganizationMember(organization_id=org.id, user_id=user.id, role="admin")
    db.add(member)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.get("/api/organizations")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_organization(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"user_{uid}@test.com", is_superuser=True)
    db.add(user)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    org_slug = f"new-org-{uid}"
    response = await client.post(
        "/api/organizations", json={"name": "New Org", "slug": org_slug}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Org"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_members(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"user_mem_{uid}@test.com")
    db.add(user)
    org_id = str(ULID())
    org = Organization(id=org_id, name="Mem Org", slug=f"mem-org-{org_id}")
    db.add(org)
    from app.models.organization import OrganizationMember

    member = OrganizationMember(organization_id=org.id, user_id=user.id, role="admin")
    db.add(member)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.get(f"/api/organizations/{org.id}/members")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_organization(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"user_upd_{uid}@test.com", is_superuser=True)
    db.add(user)
    org_id = str(ULID())
    org = Organization(id=org_id, name="Old Name", slug=f"old-org-{org_id}")
    db.add(org)
    from app.models.organization import OrganizationMember

    member = OrganizationMember(organization_id=org.id, user_id=user.id, role="admin")
    db.add(member)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.patch(
        f"/api/organizations/{org.id}", json={"name": "New Name"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_invitations(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"user_inv_{uid}@test.com", is_superuser=True)
    db.add(user)
    org_id = str(ULID())
    org = Organization(id=org_id, name="Inv Org", slug=f"inv-org-{org_id}")
    db.add(org)
    from app.models.organization import OrganizationMember

    member = OrganizationMember(organization_id=org.id, user_id=user.id, role="admin")
    db.add(member)

    from app.models.invitation import Invitation

    inv = Invitation(
        id=str(ULID()),
        organization_id=org.id,
        email="test_inv@example.com",
        invited_by_user_id=user.id,
    )
    db.add(inv)

    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.get(f"/api/organizations/{org.id}/invitations")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_accept_invitation(client: AsyncClient, db: AsyncSession):
    from ulid import ULID

    uid = str(ULID())
    user = User(id=uid, email=f"user_acc_{uid}@test.com")
    db.add(user)
    org_id = str(ULID())
    org = Organization(id=org_id, name="Acc Org", slug=f"acc-org-{org_id}")
    db.add(org)

    from app.models.invitation import Invitation

    token = f"token_{uid}"
    inv = Invitation(
        id=str(ULID()),
        organization_id=org.id,
        email=f"user_acc_{uid}@test.com",
        token=token,
        status="pending",
        invited_by_user_id=user.id,
    )
    db.add(inv)

    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.post(f"/api/invitations/{token}/accept")
    assert response.status_code == 200
    assert response.json()["message"] == "Invitation accepted"

    app.dependency_overrides.clear()
