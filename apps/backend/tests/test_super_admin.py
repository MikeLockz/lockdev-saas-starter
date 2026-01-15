from datetime import UTC

import pytest
from httpx import AsyncClient

from src.models import Organization, User


@pytest.fixture
async def test_superuser(db_session):
    import uuid

    email = f"super_admin_{uuid.uuid4()}@example.com"
    user = User(email=email, password_hash="dummy_hash", display_name="Super Admin", is_super_admin=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()


@pytest.fixture
async def superuser_token_headers(test_superuser):
    return {"Authorization": f"Bearer mock_{test_superuser.email}"}


@pytest.fixture
async def test_organization(db_session):
    import uuid

    org = Organization(
        name=f"Test Org {uuid.uuid4()}",
        subscription_status="ACTIVE",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    yield org
    await db_session.delete(org)
    await db_session.commit()


@pytest.mark.asyncio
async def test_list_organizations(client: AsyncClient, superuser_token_headers: dict, test_organization):
    """Test listing all organizations."""
    response = await client.get("/api/v1/admin/super-admin/organizations", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_organization(client: AsyncClient, superuser_token_headers: dict, test_organization):
    """Test getting a single organization."""
    response = await client.get(
        f"/api/v1/admin/super-admin/organizations/{test_organization.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_organization.name


@pytest.mark.asyncio
async def test_update_organization(client: AsyncClient, superuser_token_headers: dict, test_organization):
    """Test updating an organization."""
    response = await client.patch(
        f"/api/v1/admin/super-admin/organizations/{test_organization.id}",
        headers=superuser_token_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert not response.json()["is_active"]


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, superuser_token_headers: dict):
    """Test listing all users."""
    response = await client.get("/api/v1/admin/super-admin/users", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_unlock_user(client: AsyncClient, superuser_token_headers: dict, db_session):
    """Test unlocking a locked user."""
    import uuid
    from datetime import datetime, timedelta

    # Create a locked user
    locked_user = User(
        email=f"locked_{uuid.uuid4()}@example.com",
        password_hash="dummy_hash",
        display_name="Locked User",
        locked_until=datetime.now(UTC) + timedelta(hours=1),
        failed_login_attempts=5,
    )
    db_session.add(locked_user)
    await db_session.commit()
    await db_session.refresh(locked_user)

    # Unlock
    response = await client.patch(
        f"/api/v1/admin/super-admin/users/{locked_user.id}/unlock", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["success"]

    # Cleanup
    await db_session.delete(locked_user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_system_health(client: AsyncClient, superuser_token_headers: dict):
    """Test system health endpoint."""
    response = await client.get("/api/v1/admin/super-admin/system", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "db_status" in data
    assert "redis_status" in data
    assert "metrics" in data


@pytest.mark.asyncio
async def test_super_admin_unauthorized(client: AsyncClient, test_user_token_headers: dict):
    """Test that non-super-admin users cannot access super admin endpoints."""
    response = await client.get("/api/v1/admin/super-admin/organizations", headers=test_user_token_headers)
    assert response.status_code == 403
