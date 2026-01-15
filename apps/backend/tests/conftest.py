from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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
        # Rollback any uncommitted changes for test isolation
        await session.rollback()


@pytest.fixture(autouse=True)
def mock_presidio():
    from unittest.mock import MagicMock

    with patch("src.logging.get_analyzer_engine") as mock_engine:
        mock_instance = MagicMock()
        mock_instance.analyze.return_value = []
        mock_engine.return_value = mock_instance
        yield mock_engine


@pytest.fixture(autouse=True)
def reset_context_vars():
    from src.database import tenant_id_ctx, user_id_ctx

    token_user = user_id_ctx.set(None)
    token_tenant = tenant_id_ctx.set(None)

    yield

    user_id_ctx.reset(token_user)
    tenant_id_ctx.reset(token_tenant)


@pytest.fixture
async def client() -> AsyncClient:
    from httpx import ASGITransport

    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        yield client


@pytest.fixture
async def test_user(db_session):
    import uuid

    from src.models import User

    email = f"test_user_{uuid.uuid4()}@example.com"
    user = User(
        email=email,
        password_hash="dummy_hash",
        display_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    yield user

    # Cleanup handled by session rollback in db_session fixture


@pytest.fixture
async def test_user_token_headers(test_user):
    # In local env, auth.py accepts "mock_{email}" as a valid token
    return {"Authorization": f"Bearer mock_{test_user.email}"}


@pytest.fixture
async def test_organization(db_session):
    """Create a test organization."""
    import uuid

    from src.models.organizations import Organization

    org = Organization(
        id=uuid.uuid4(),
        name="Test Organization",
        timezone="America/New_York",
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    yield org


@pytest.fixture
async def test_patient(db_session, test_organization):
    """Create a test patient."""
    import uuid
    from datetime import date

    from src.models.organizations import OrganizationPatient
    from src.models.profiles import Patient

    patient = Patient(
        id=uuid.uuid4(),
        first_name="Test",
        last_name="Patient",
        dob=date(1990, 1, 1),
        legal_sex="F",
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)

    # Link patient to organization
    org_patient = OrganizationPatient(
        organization_id=test_organization.id,
        patient_id=patient.id,
        status="ACTIVE",
    )
    db_session.add(org_patient)
    await db_session.commit()

    yield patient


@pytest.fixture
async def test_provider(db_session, test_organization, test_user):
    """Create a test provider."""
    import uuid

    from src.models.profiles import Provider

    provider = Provider(
        id=uuid.uuid4(),
        user_id=test_user.id,
        organization_id=test_organization.id,
        npi_number="1234567890",
        specialty="General Practice",
    )
    db_session.add(provider)
    await db_session.commit()
    await db_session.refresh(provider)
    yield provider


@pytest.fixture
async def test_provider_2(db_session, test_organization):
    """Create a second test provider."""
    import uuid

    from src.models import User
    from src.models.profiles import Provider

    # Create a second user for the second provider
    email = f"test_provider2_{uuid.uuid4()}@example.com"
    user2 = User(
        email=email,
        password_hash="dummy_hash",
        display_name="Test Provider 2",
    )
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    provider2 = Provider(
        id=uuid.uuid4(),
        user_id=user2.id,
        organization_id=test_organization.id,
        npi_number="0987654321",
        specialty="Cardiology",
    )
    db_session.add(provider2)
    await db_session.commit()
    await db_session.refresh(provider2)
    yield provider2
