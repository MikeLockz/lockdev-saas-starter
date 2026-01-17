import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def db():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import NullPool

    from app.core.config import settings

    test_engine = create_async_engine(
        settings.sqlalchemy_database_uri, poolclass=NullPool
    )
    async with (
        test_engine.connect() as connection,
        AsyncSession(bind=connection, expire_on_commit=False) as session,
    ):
        yield session
        await session.rollback()
    await test_engine.dispose()
