import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.operations import Call
from src.config import settings

# Fixtures assumed available: client, test_db, test_org, test_user_token_headers

@pytest.mark.asyncio
async def test_create_call(client: AsyncClient, test_org, test_user_token_headers):
    response = await client.post(
        f"{settings.API_V1_STR}/organizations/{test_org.id}/calls/",
        json={
            "direction": "INBOUND",
            "phone_number": "+15551234567",
            "notes": "Test call"
        },
        headers=test_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["organization_id"] == str(test_org.id)
    assert data["phone_number"] == "+15551234567"

@pytest.mark.asyncio
async def test_list_calls(client: AsyncClient, test_org, test_user_token_headers):
    # Log a call first
    call_res = await client.post(
        f"{settings.API_V1_STR}/organizations/{test_org.id}/calls/",
        json={"direction": "OUTBOUND", "phone_number": "+19999999999"},
        headers=test_user_token_headers
    )
    assert call_res.status_code == 200
    
    response = await client.get(
        f"{settings.API_V1_STR}/organizations/{test_org.id}/calls/",
        headers=test_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["direction"] == "OUTBOUND"

@pytest.mark.asyncio
async def test_update_call_completion(client: AsyncClient, test_org, test_user_token_headers):
    # Create
    call_res = await client.post(
        f"{settings.API_V1_STR}/organizations/{test_org.id}/calls/",
        json={"direction": "INBOUND", "phone_number": "+123"},
        headers=test_user_token_headers
    )
    call_id = call_res.json()["id"]
    
    # Update to COMPLETED
    response = await client.patch(
        f"{settings.API_V1_STR}/organizations/{test_org.id}/calls/{call_id}",
        json={"status": "COMPLETED", "outcome": "RESOLVED"},
        headers=test_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["ended_at"] is not None
    assert data["duration_seconds"] is not None
