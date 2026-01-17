import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


@pytest.mark.asyncio
async def test_statement_timeout():
    """
    Verify that the database correctly enforces statement timeouts.
    """
    # Create a test engine with short timeout
    test_engine = create_async_engine(
        settings.sqlalchemy_database_uri,
        connect_args={"server_settings": {"statement_timeout": "250ms"}},
    )

    try:
        async with test_engine.connect() as conn:
            with pytest.raises(DBAPIError) as excinfo:
                # Sleep for 1 second, which is > 250ms
                await conn.execute(text("SELECT pg_sleep(1)"))

            # Check if the error is indeed a query cancel/timeout
            # Postgres error message: canceling statement due to statement timeout
            assert "canceling statement due to statement timeout" in str(excinfo.value)
    finally:
        await test_engine.dispose()
