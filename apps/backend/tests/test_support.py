import pytest
from httpx import AsyncClient

from src.models import User


@pytest.fixture
async def test_superuser(db_session):
    import uuid

    email = f"admin_{uuid.uuid4()}@example.com"
    user = User(email=email, password_hash="dummy_hash", display_name="Admin User", is_super_admin=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()


@pytest.fixture
async def superuser_token_headers(test_superuser):
    return {"Authorization": f"Bearer mock_{test_superuser.email}"}


@pytest.mark.asyncio
async def test_create_ticket(client: AsyncClient, test_user_token_headers: dict):
    response = await client.post(
        "/api/v1/support/tickets",
        headers=test_user_token_headers,
        json={
            "subject": "Help me",
            "category": "TECHNICAL",
            "priority": "MEDIUM",
            "initial_message": "I have an issue",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "Help me"
    assert data["status"] == "OPEN"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["body"] == "I have an issue"


@pytest.mark.asyncio
async def test_get_tickets(client: AsyncClient, test_user_token_headers: dict):
    # Create one first
    await client.post(
        "/api/v1/support/tickets",
        headers=test_user_token_headers,
        json={"subject": "Ticket A", "category": "BILLING", "priority": "LOW", "initial_message": "Bill is wrong"},
    )

    response = await client.get("/api/v1/support/tickets", headers=test_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(t["subject"] == "Ticket A" for t in data)


@pytest.mark.asyncio
async def test_add_message(client: AsyncClient, test_user_token_headers: dict):
    # Create ticket
    r = await client.post(
        "/api/v1/support/tickets",
        headers=test_user_token_headers,
        json={"subject": "Chat", "category": "OTHER", "priority": "LOW", "initial_message": "Hello"},
    )
    ticket_id = r.json()["id"]

    # Add message
    r2 = await client.post(
        f"/api/v1/support/tickets/{ticket_id}/messages",
        headers=test_user_token_headers,
        json={"body": "Follow up", "is_internal": False},
    )
    assert r2.status_code == 200

    # Verify
    r3 = await client.get(f"/api/v1/support/tickets/{ticket_id}", headers=test_user_token_headers)
    msgs = r3.json()["messages"]
    assert len(msgs) == 2
    assert msgs[1]["body"] == "Follow up"


@pytest.mark.asyncio
async def test_admin_flow(client: AsyncClient, test_user_token_headers: dict, superuser_token_headers: dict):
    # User creates ticket
    r = await client.post(
        "/api/v1/support/tickets",
        headers=test_user_token_headers,
        json={"subject": "Admin Test", "category": "ACCOUNT", "priority": "HIGH", "initial_message": "Pls fix"},
    )
    ticket_id = r.json()["id"]

    # Admin sees it
    r_adm = await client.get("/api/v1/support/admin/tickets", headers=superuser_token_headers)
    assert r_adm.status_code == 200
    all_tickets = r_adm.json()
    assert any(t["id"] == ticket_id for t in all_tickets)

    # Admin adds internal note
    r_note = await client.post(
        f"/api/v1/support/tickets/{ticket_id}/messages",
        headers=superuser_token_headers,
        json={"body": "Secret note", "is_internal": True},
    )
    assert r_note.status_code == 200

    # User should NOT see internal note
    r_user_view = await client.get(f"/api/v1/support/tickets/{ticket_id}", headers=test_user_token_headers)
    user_msgs = r_user_view.json()["messages"]
    assert not any(m["body"] == "Secret note" for m in user_msgs)

    # Admin SHOULD see internal note
    r_admin_view = await client.get(f"/api/v1/support/tickets/{ticket_id}", headers=superuser_token_headers)
    admin_msgs = r_admin_view.json()["messages"]
    assert any(m["body"] == "Secret note" for m in admin_msgs)

    # Admin updates status
    r_patch = await client.patch(
        f"/api/v1/support/admin/tickets/{ticket_id}", headers=superuser_token_headers, json={"status": "RESOLVED"}
    )
    assert r_patch.status_code == 200
    assert r_patch.json()["status"] == "RESOLVED"
    assert r_patch.json()["resolved_at"] is not None


@pytest.mark.asyncio
async def test_security(client: AsyncClient, test_user_token_headers: dict):
    # Try to access admin route as user
    r = await client.get("/api/v1/support/admin/tickets", headers=test_user_token_headers)
    assert r.status_code == 403
