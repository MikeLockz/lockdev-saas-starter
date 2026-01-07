from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models import User
from src.security.auth import get_current_user


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as c:
        yield c


@pytest.fixture
async def admin_user(db_session):
    email = f"admin-{uuid4().hex[:8]}@example.com"
    user = User(email=email, password_hash="hash", display_name="Admin User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def invited_user(db_session):
    email = f"invited-{uuid4().hex[:8]}@example.com"
    user = User(email=email, password_hash="hash", display_name="Invited User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_invite_flow(client, admin_user, invited_user, db_session):
    # Mock enqueue_task
    from unittest.mock import AsyncMock, patch

    with patch("src.api.organizations.enqueue_task", new_callable=AsyncMock) as mock_enqueue:
        # 1. Login as Admin
        app.dependency_overrides[get_current_user] = lambda: admin_user

        # 2. Create Org
        response = await client.post("/api/v1/organizations", json={"name": "Invite Org", "tax_id": "99-9999999"})
        assert response.status_code == 200, f"Create Org failed: {response.text}"
        org_id = response.json()["id"]

        # 3. Create Invitation
        invite_data = {"email": invited_user.email, "role": "PROVIDER"}
        response = await client.post(f"/api/v1/organizations/{org_id}/invitations", json=invite_data)
        assert response.status_code == 200, f"Invite failed: {response.text}"

        # Verify enqueue was called
        mock_enqueue.assert_called_once()
        invite = response.json()
        assert invite["email"] == invited_user.email
        token = invite["token"]

        # 4. List Invitations
    response = await client.get(f"/api/v1/organizations/{org_id}/invitations")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # 5. Get Invitation Publicly
    app.dependency_overrides = {}  # Logout
    response = await client.get(f"/api/v1/invitations/{token}")
    assert response.status_code == 200
    assert response.json()["organization_id"] == org_id

    # 6. Accept Invitation
    app.dependency_overrides[get_current_user] = lambda: invited_user
    response = await client.post(f"/api/v1/invitations/{token}/accept")
    assert response.status_code == 200, f"Accept failed: {response.text}"
    assert response.json()["status"] == "ACCEPTED"

    # 7. Verify Membership
    response = await client.get("/api/v1/organizations")
    orgs = response.json()
    assert any(o["id"] == org_id for o in orgs)

    # Clean up overrides
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_invite_permissions(client, admin_user, invited_user):
    # 1. Login as Admin
    app.dependency_overrides[get_current_user] = lambda: admin_user
    response = await client.post("/api/v1/organizations", json={"name": "Perm Org", "tax_id": "88-8888888"})
    org_id = response.json()["id"]

    # 2. Login as Random User (Not member)
    app.dependency_overrides[get_current_user] = lambda: invited_user
    invite_data = {"email": "someone@example.com", "role": "STAFF"}

    # Try to invite
    response = await client.post(f"/api/v1/organizations/{org_id}/invitations", json=invite_data)
    assert response.status_code == 403

    # Clean up
    app.dependency_overrides = {}
