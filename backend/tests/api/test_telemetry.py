import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.db import get_db
from app.main import app
from app.models.user import User


@pytest.mark.asyncio
async def test_track_telemetry(client: AsyncClient, db: AsyncSession):
    user = User(id="user_tel_1", email="tel@test.com")
    db.add(user)
    await db.flush()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db

    response = await client.post(
        "/api/telemetry", json={"event": "test_event", "properties": {"foo": "bar"}}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "recorded"

    app.dependency_overrides.clear()
