import pytest
import asyncio
from unittest.mock import patch
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings
from src.models import Base

# Use the configured database URL (assuming it points to a test/dev DB)
TEST_DATABASE_URL = settings.DATABASE_URL

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    # Don't drop schema - migrations are already applied
    # Just ensure tables exist (checkfirst=True by default)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Don't clean up - leave DB state for inspection
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture(autouse=True)
def mock_presidio():
    from unittest.mock import MagicMock
    with patch("src.logging.get_analyzer_engine") as mock_engine:
        mock_instance = MagicMock()
        # Mock analyze method to return empty list or whatever minimal needed
        mock_instance.analyze.return_value = []
        mock_engine.return_value = mock_instance
        yield mock_engine
