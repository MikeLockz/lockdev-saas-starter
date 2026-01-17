import pytest
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.db import receive_reset


@pytest.mark.asyncio
async def test_connection_cleanup():
    # Create a fresh engine for this test
    test_engine = create_async_engine(settings.sqlalchemy_database_uri)
    # Attach the same reset listener used in the app
    event.listen(test_engine.sync_engine, "reset", receive_reset)

    test_async_session_local = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    # 1. Get session and set variable
    async with test_async_session_local() as session1:
        await session1.execute(
            text("SELECT set_config('app.current_tenant_id', 'test_cleanup', false)")
        )
        await session1.commit()
        # Get the connection ID to verify reuse
        result = await session1.execute(text("SELECT pg_backend_pid()"))
        pid1 = result.scalar()

    # 2. Session1 is closed/returned to pool.

    # 3. Get new session. Hopefully reusing same connection.
    # To increase chance of reuse, we do this sequentially.
    async with test_async_session_local() as session2:
        result = await session2.execute(text("SELECT pg_backend_pid()"))
        pid2 = result.scalar()

        # We only test cleanup if we got the same connection
        if pid1 == pid2:
            # Check variable
            result = await session2.execute(
                text("SELECT current_setting('app.current_tenant_id', true)")
            )
            val = result.scalar()

            # If DISCARD ALL is working, val should be None or default.
            # It definitely should NOT be 'test_cleanup'
            assert val != "test_cleanup", "Session variable persisted!"
            assert val is None or val == "", f"Variable reset to: {val}"
        else:
            pytest.skip("Could not reuse the same connection, skipping cleanup test")

    await test_engine.dispose()
