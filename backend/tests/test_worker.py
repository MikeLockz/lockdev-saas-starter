from unittest.mock import patch

import pytest

from app.worker import (
    cleanup_expired_sessions,
    enforce_data_retention,
    health_check_task,
)


@pytest.mark.asyncio
async def test_health_check_task():
    res = await health_check_task({})
    assert res == "OK"


@pytest.mark.asyncio
async def test_cleanup_expired_sessions(db):
    # Mock AsyncSessionLocal to return our test db session
    with patch("app.worker.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = db
        res = await cleanup_expired_sessions({})
        assert "Cleaned up" in res


@pytest.mark.asyncio
async def test_enforce_data_retention(db):
    # Mock AsyncSessionLocal to return our test db session
    with patch("app.worker.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = db
        res = await enforce_data_retention({})
        assert "Cleaned up" in res
