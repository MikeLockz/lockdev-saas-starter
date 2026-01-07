from collections.abc import AsyncGenerator
from contextvars import ContextVar

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from src.config import settings
from src.logging import request_id_ctx

# ContextVars for RLS
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
tenant_id_ctx: ContextVar[str | None] = ContextVar("tenant_id", default=None)

# Create Async Engine
engine = create_async_engine(
    settings.DATABASE_URL, echo=(settings.ENVIRONMENT == "local"), pool_pre_ping=True, future=True
)

# Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Event Listeners


# Prevent connection pool leakage by discarding session state on checkin
@event.listens_for(engine.sync_engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    if dbapi_connection is None:
        return
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("ROLLBACK")
        cursor.execute("RESET ALL")
    except Exception:
        # In case connection is dead
        pass
    finally:
        cursor.close()


# RLS Setup
@event.listens_for(Session, "after_begin")
def receive_after_begin(session, transaction, connection):
    uid = user_id_ctx.get()
    tid = tenant_id_ctx.get()

    if uid or tid:
        # Sanitize input or trust ContextVars (internal use)
        # Using string interpolation for SET commands is standard for Postgres session vars if properly validated
        # But better to use parameters if possible.
        # set_config(name, value, is_local) is better: SELECT set_config('app.current_user_id', :uid, false)

        if connection:
            if uid:
                connection.execute(text("SELECT set_config('app.current_user_id', :uid, false)"), {"uid": str(uid)})

            if tid:
                connection.execute(text("SELECT set_config('app.current_tenant_id', :tid, false)"), {"tid": str(tid)})


# DB Tracing: Inject request_id
@event.listens_for(engine.sync_engine, "before_cursor_execute", retval=True)
def comment_sql(conn, cursor, statement, parameters, context, executemany):
    rid = request_id_ctx.get()
    if rid and rid != "unknown":
        statement = f"{statement} -- request_id={rid}"
    return statement, parameters
