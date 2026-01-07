import pytest
from httpx import AsyncClient

from src.models.organizations import Organization, OrganizationMember


@pytest.fixture
async def test_org(db_session, test_user):
    """Create a test organization and add user as member."""
    org = Organization(name="Messaging Test Org")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    member = OrganizationMember(organization_id=org.id, user_id=test_user.id, role="MEMBER")
    db_session.add(member)
    await db_session.commit()

    return org


@pytest.fixture
async def other_user(db_session):
    """Create another user for messaging."""
    import uuid

    from src.models import User

    email = f"other_{uuid.uuid4()}@example.com"
    user = User(
        email=email,
        password_hash="dummy",
        display_name="Other User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_thread(client: AsyncClient, test_user_token_headers: dict, test_org, other_user):
    response = await client.post(
        "/api/v1/users/me/threads",
        json={
            "organization_id": str(test_org.id),
            "subject": "Test Thread",
            "initial_message": "Hello world",
            "participant_ids": [str(other_user.id)],
        },
        headers=test_user_token_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "Test Thread"
    assert data["last_message"]["body"] == "Hello world"
    assert len(data["participants"]) >= 2  # Creator + Other


@pytest.mark.asyncio
async def test_list_threads(client: AsyncClient, test_user_token_headers: dict, test_org, other_user):
    # Ensure thread exists (create one)
    await client.post(
        "/api/v1/users/me/threads",
        json={
            "organization_id": str(test_org.id),
            "subject": "List Test",
            "initial_message": "Hi",
            "participant_ids": [str(other_user.id)],
        },
        headers=test_user_token_headers,
    )

    response = await client.get(
        "/api/v1/users/me/threads",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["subject"] == "List Test"


@pytest.mark.asyncio
async def test_send_message(client: AsyncClient, test_user_token_headers: dict, test_org, other_user):
    # Create thread
    resp = await client.post(
        "/api/v1/users/me/threads",
        json={
            "organization_id": str(test_org.id),
            "subject": "Msg Test",
            "initial_message": "Init",
            "participant_ids": [str(other_user.id)],
        },
        headers=test_user_token_headers,
    )
    thread_id = resp.json()["id"]

    # Send message
    response = await client.post(
        f"/api/v1/users/me/threads/{thread_id}/messages",
        json={"body": "Reply message"},
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["body"] == "Reply message"
    assert data["sender_name"] == "Test User"


@pytest.mark.asyncio
async def test_get_thread(client: AsyncClient, test_user_token_headers: dict, test_org, other_user):
    # Create thread
    resp = await client.post(
        "/api/v1/users/me/threads",
        json={
            "organization_id": str(test_org.id),
            "subject": "Get Test",
            "initial_message": "Init",
            "participant_ids": [str(other_user.id)],
        },
        headers=test_user_token_headers,
    )
    thread_id = resp.json()["id"]

    response = await client.get(
        f"/api/v1/users/me/threads/{thread_id}",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == thread_id
    assert data["subject"] == "Get Test"
