from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Construct database URL
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # Set to True for debugging SQL
    future=True,
)


@event.listens_for(engine.sync_engine, "checkin")
def receive_checkin(_dbapi_connection, _connection_record):
    """
    Ensure the connection is clean when returned to the pool.
    """


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
