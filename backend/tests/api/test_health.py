import pytest

from app.core.db import get_db
from app.main import app


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_deep(client, db):
    app.dependency_overrides[get_db] = lambda: db
    response = await client.get("/health/deep")
    assert response.status_code == 200
    assert response.json()["components"]["database"] == "ok"
    app.dependency_overrides.clear()
