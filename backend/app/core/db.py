import logging
from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger(__name__)

# Construct database URL
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # Set to True for debugging SQL
    future=True,
    # DB-004: Disable statement cache to allow DISCARD ALL working with asyncpg
    connect_args={"statement_cache_size": 0},
)


@event.listens_for(engine.sync_engine, "reset")
def receive_reset(dbapi_connection, _connection_record, _reset_state=None):
    """
    Ensure the connection is clean when returned to the pool.
    """
    cursor = dbapi_connection.cursor()
    try:
        # Ensure we are not in a failed transaction state
        cursor.execute("ROLLBACK")
        cursor.execute("DISCARD ALL")
    except Exception as e:
        logger.error(f"DISCARD ALL FAILED: {e}")
    finally:
        cursor.close()


@event.listens_for(engine.sync_engine, "begin")
def receive_begin(_conn):
    """
    Placeholder for RLS session variables.
    Will be fully implemented once Auth context is available.
    """


@event.listens_for(engine.sync_engine, "before_cursor_execute", retval=True)
def add_request_id_comment(
    _conn, _cursor, statement, parameters, _context, _executemany
):
    from app.core.middleware import request_id_var

    rid = request_id_var.get()
    if rid:
        statement = f"/* rid: {rid} */ {statement}"
    return statement, parameters


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
