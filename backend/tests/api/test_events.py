import pytest

from app.core.auth import get_current_user
from app.main import app


@pytest.mark.asyncio
async def test_stream_events_unauthorized(client):
    """
    Verify that the SSE endpoint rejects unauthenticated requests.
    """
    # Ensure no overrides are active
    app.dependency_overrides.pop(get_current_user, None)

    response = await client.get("/api/events")
    # Should fail with 401 Unauthorized (or 403 depending on implementation)
    assert response.status_code in [401, 403]
