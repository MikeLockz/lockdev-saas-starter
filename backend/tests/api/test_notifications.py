from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.models.communications import Notification


@pytest.fixture
async def user_notification(db_session, test_user):
    """Create a sample notification for the test user."""
    notification = Notification(
        user_id=test_user.id,
        type="SYSTEM",
        title="Test Notification",
        body="This is a test notification",
        is_read=False,
    )
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)
    return notification


@pytest.mark.asyncio
async def test_list_notifications(
    client: AsyncClient, 
    test_user_token_headers: dict, 
    user_notification: Notification
):
    response = await client.get(
        "/api/v1/users/me/notifications",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["id"] == str(user_notification.id)
    assert data["items"][0]["title"] == "Test Notification"


@pytest.mark.asyncio
async def test_get_unread_count(
    client: AsyncClient, 
    test_user_token_headers: dict, 
    user_notification: Notification
):
    response = await client.get(
        "/api/v1/users/me/notifications/unread-count",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1


@pytest.mark.asyncio
async def test_mark_as_read(
    client: AsyncClient, 
    test_user_token_headers: dict, 
    user_notification: Notification
):
    response = await client.patch(
        f"/api/v1/users/me/notifications/{user_notification.id}/read",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["read_at"] is not None


@pytest.mark.asyncio
async def test_mark_as_unread(
    client: AsyncClient, 
    test_user_token_headers: dict, 
    user_notification: Notification
):
    # First mark as read
    user_notification.is_read = True
    
    response = await client.patch(
        f"/api/v1/users/me/notifications/{user_notification.id}/unread",
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is False
    assert data["read_at"] is None


@pytest.mark.asyncio
async def test_mark_all_read(
    client: AsyncClient, 
    test_user_token_headers: dict, 
    user_notification: Notification,
    db_session
):
    # Create another notification
    notif2 = Notification(
        user_id=user_notification.user_id,
        type="SYSTEM",
        title="Second Notification",
        is_read=False,
    )
    db_session.add(notif2)
    await db_session.commit()

    response = await client.post(
        "/api/v1/users/me/notifications/mark-all-read",
        headers=test_user_token_headers,
    )
    assert response.status_code == 204

    # Verify all are read
    # We need to refresh instances or query DB
    await db_session.refresh(user_notification)
    await db_session.refresh(notif2)
    assert user_notification.is_read is True
    assert notif2.is_read is True


@pytest.mark.asyncio
async def test_delete_notification(
    client: AsyncClient, 
    test_user_token_headers: dict, 
    user_notification: Notification,
    db_session
):
    response = await client.delete(
        f"/api/v1/users/me/notifications/{user_notification.id}",
        headers=test_user_token_headers,
    )
    assert response.status_code == 204

    # Verify deleted
    response = await client.get(
        "/api/v1/users/me/notifications",
        headers=test_user_token_headers,
    )
    data = response.json()
    # Should not find the deleted notification
    ids = [item["id"] for item in data["items"]]
    assert str(user_notification.id) not in ids
