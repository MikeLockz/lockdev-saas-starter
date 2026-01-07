import pytest
from httpx import AsyncClient

from src.config import settings


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, test_org, test_user, test_user_token_headers):
    response = await client.post(
        f"{settings.API_V1_STR}/organizations/{test_org.id}/tasks/",
        json={"title": "Follow up with patient", "priority": "HIGH", "assignee_id": str(test_user.id)},
        headers=test_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Follow up with patient"
    assert data["status"] == "TODO"


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, test_org, test_user_token_headers):
    response = await client.get(
        f"{settings.API_V1_STR}/organizations/{test_org.id}/tasks/", headers=test_user_token_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_my_tasks(client: AsyncClient, test_org, test_user, test_user_token_headers):
    # Ensure a task exists
    await client.post(
        f"{settings.API_V1_STR}/organizations/{test_org.id}/tasks/",
        json={"title": "My Task", "priority": "LOW", "assignee_id": str(test_user.id)},
        headers=test_user_token_headers,
    )

    response = await client.get(f"{settings.API_V1_STR}/users/tasks/me/all", headers=test_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "My Task"
