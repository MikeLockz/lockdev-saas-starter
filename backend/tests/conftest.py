import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import postgresql_audit
import pytest

# Monkeypatch versioning_manager BEFORE importing app to prevent listener attachment
postgresql_audit.versioning_manager.init = MagicMock()
# Provide a dummy activity_cls with __table__ to avoid AttributeErrors
mock_activity_cls = MagicMock()
mock_activity_cls.__table__ = MagicMock()
postgresql_audit.versioning_manager.activity_cls = mock_activity_cls

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


class _DbState:
    """Simple holder to avoid using global statement."""

    initialized: bool = False


_db_state = _DbState()


@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    if _db_state.initialized:
        yield
        return

    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import create_async_engine

    from app.core.config import settings
    from app.core.models_base import Base

    engine = create_async_engine(settings.sqlalchemy_database_uri)
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

        # Manually enable RLS and add policies (extracted from migrations)
        tables_simple = [
            "patients",
            "providers",
            "staff",
            "proxies",
            "appointments",
            "documents",
            "tasks",
            "call_logs",
            "support_tickets",
            "invitations",
        ]
        for table in tables_simple:
            await conn.execute(
                sa.text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
            )
            await conn.execute(
                sa.text(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
            )
            await conn.execute(
                sa.text(f"""
                CREATE POLICY tenant_isolation_{table} ON {table}
                USING (organization_id = current_setting('app.current_tenant_id', TRUE))
            """)
            )

        # Joined scoped tables
        await conn.execute(
            sa.text("ALTER TABLE contact_methods ENABLE ROW LEVEL SECURITY")
        )
        await conn.execute(
            sa.text(
                "DROP POLICY IF EXISTS "
                "tenant_isolation_contact_methods ON contact_methods"
            )
        )
        await conn.execute(
            sa.text(
                """
            CREATE POLICY tenant_isolation_contact_methods ON contact_methods
            USING (
                EXISTS (
                    SELECT 1 FROM patients
                    WHERE patients.id = contact_methods.patient_id
                    AND patients.organization_id =
                        current_setting('app.current_tenant_id', TRUE)
                )
            )
        """
            )
        )

        await conn.execute(
            sa.text("ALTER TABLE care_team_assignments ENABLE ROW LEVEL SECURITY")
        )
        await conn.execute(
            sa.text(
                "DROP POLICY IF EXISTS "
                "tenant_isolation_care_team_assignments ON care_team_assignments"
            )
        )
        await conn.execute(
            sa.text(
                """
            CREATE POLICY tenant_isolation_care_team_assignments
                ON care_team_assignments
            USING (
                EXISTS (
                    SELECT 1 FROM patients
                    WHERE patients.id = care_team_assignments.patient_id
                    AND patients.organization_id =
                        current_setting('app.current_tenant_id', TRUE)
                )
            )
        """
            )
        )

    _db_state.initialized = True
    yield
    await engine.dispose()


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
