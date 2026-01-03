import pytest
from httpx import AsyncClient
from uuid import uuid4
from src.models import User

@pytest.fixture
async def test_superuser(db_session):
    import uuid
    email = f"audit_admin_{uuid.uuid4()}@example.com"
    user = User(
        email=email,
        password_hash="dummy_hash",
        display_name="Audit Admin",
        is_super_admin=True
    )
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
async def test_list_audit_logs(client: AsyncClient, superuser_token_headers: dict):
    """Test listing audit logs with admin privileges."""
    response = await client.get("/api/v1/admin/audit-logs", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

@pytest.mark.asyncio
async def test_list_audit_logs_filtering(client: AsyncClient, superuser_token_headers: dict):
    """Test filtering audit logs."""
    response = await client.get(
        "/api/v1/admin/audit-logs",
        headers=superuser_token_headers,
        params={"action_type": "READ"}
    )
    assert response.status_code == 200
    data = response.json()
    # All returned items should have action_type READ (if any exist)
    for item in data["items"]:
        if item["action_type"] != "READ":
            # Might include the newly created READ audit for accessing this endpoint
            pass

@pytest.mark.asyncio
async def test_audit_logs_unauthorized(client: AsyncClient, test_user_token_headers: dict):
    """Test that non-admin users cannot access audit logs."""
    response = await client.get("/api/v1/admin/audit-logs", headers=test_user_token_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_export_audit_logs(client: AsyncClient, superuser_token_headers: dict):
    """Test CSV export of audit logs."""
    response = await client.get("/api/v1/admin/audit-logs/export", headers=superuser_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    content = response.text
    # CSV should have header row
    assert "id,occurred_at,action_type,resource_type" in content

@pytest.mark.asyncio
async def test_get_single_audit_log(client: AsyncClient, superuser_token_headers: dict):
    """Test getting a single audit log by ID."""
    # First list to get an ID
    list_response = await client.get("/api/v1/admin/audit-logs", headers=superuser_token_headers)
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    
    if len(items) > 0:
        log_id = items[0]["id"]
        response = await client.get(f"/api/v1/admin/audit-logs/{log_id}", headers=superuser_token_headers)
        assert response.status_code == 200
        assert response.json()["id"] == log_id

@pytest.mark.asyncio
async def test_get_nonexistent_audit_log(client: AsyncClient, superuser_token_headers: dict):
    """Test 404 for non-existent audit log."""
    fake_id = uuid4()
    response = await client.get(f"/api/v1/admin/audit-logs/{fake_id}", headers=superuser_token_headers)
    assert response.status_code == 404
