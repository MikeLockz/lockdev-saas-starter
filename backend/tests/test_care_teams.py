"""Tests for Care Team API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime, timezone
from src.main import app
from src.models import User, Organization, OrganizationMember, Provider
from src.models.profiles import Patient
from src.models.organizations import OrganizationPatient
from src.security.auth import get_current_user


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as c:
        yield c


@pytest.fixture
async def test_user(db_session):
    """Create a test admin user."""
    unique_email = f"careteam-admin-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Care Team Admin",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def provider_user(db_session):
    """Create a user to be a provider."""
    unique_email = f"provider-doc-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Dr. Test Provider",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def second_provider_user(db_session):
    """Create another user to be a provider."""
    unique_email = f"provider-doc2-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Dr. Second Provider",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_org(db_session, test_user):
    """Create organization with test user as admin."""
    now = datetime.now(timezone.utc)
    org = Organization(
        name="Care Team Test Practice",
        created_at=now,
        updated_at=now,
    )
    db_session.add(org)
    await db_session.flush()
    
    membership = OrganizationMember(
        organization_id=org.id,
        user_id=test_user.id,
        role="ADMIN",
        created_at=now,
        updated_at=now,
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def test_patient(db_session, test_org):
    """Create a test patient enrolled in the org."""
    now = datetime.now(timezone.utc)
    patient = Patient(
        first_name="Test",
        last_name="Patient",
        dob=datetime(1990, 1, 15).date(),
        created_at=now,
        updated_at=now,
    )
    db_session.add(patient)
    await db_session.flush()
    
    enrollment = OrganizationPatient(
        organization_id=test_org.id,
        patient_id=patient.id,
        status="ACTIVE",
        enrolled_at=now,
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


@pytest.fixture
async def test_provider(db_session, test_org, provider_user):
    """Create a provider in the org."""
    now = datetime.now(timezone.utc)
    provider = Provider(
        user_id=provider_user.id,
        organization_id=test_org.id,
        npi_number="1234567893",
        specialty="Internal Medicine",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(provider)
    await db_session.commit()
    await db_session.refresh(provider)
    return provider


@pytest.fixture
async def second_provider(db_session, test_org, second_provider_user):
    """Create a second provider in the org."""
    now = datetime.now(timezone.utc)
    provider = Provider(
        user_id=second_provider_user.id,
        organization_id=test_org.id,
        specialty="Cardiology",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(provider)
    await db_session.commit()
    await db_session.refresh(provider)
    return provider


@pytest.fixture
async def authenticated_client(client, test_user):
    """Client authenticated as test admin."""
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides = {}


class TestCareTeamAPI:
    """Test Care Team API endpoints."""

    @pytest.mark.asyncio
    async def test_assign_provider_to_care_team(
        self, authenticated_client, test_org, test_patient, test_provider
    ):
        """Test assigning a provider to a patient's care team."""
        data = {
            "provider_id": str(test_provider.id),
            "role": "PRIMARY"
        }
        response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json=data
        )
        assert response.status_code == 201, f"Response: {response.text}"
        
        result = response.json()
        assert result["role"] == "PRIMARY"
        assert result["provider_id"] == str(test_provider.id)
        assert result["provider"]["specialty"] == "Internal Medicine"

    @pytest.mark.asyncio
    async def test_get_care_team(
        self, authenticated_client, test_org, test_patient, test_provider
    ):
        """Test getting a patient's care team."""
        # First assign provider
        await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json={"provider_id": str(test_provider.id), "role": "PRIMARY"}
        )
        
        # Get care team
        response = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["patient_id"] == str(test_patient.id)
        assert len(result["members"]) >= 1
        assert result["primary_provider"] is not None

    @pytest.mark.asyncio
    async def test_only_one_primary_allowed(
        self, authenticated_client, test_org, test_patient, test_provider, second_provider
    ):
        """Test that only one PRIMARY provider is allowed."""
        # Assign first provider as PRIMARY
        response1 = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json={"provider_id": str(test_provider.id), "role": "PRIMARY"}
        )
        assert response1.status_code == 201
        
        # Try to assign second provider as PRIMARY
        response2 = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json={"provider_id": str(second_provider.id), "role": "PRIMARY"}
        )
        assert response2.status_code == 409, f"Response: {response2.text}"
        assert "PRIMARY" in response2.text

    @pytest.mark.asyncio
    async def test_multiple_specialists_allowed(
        self, authenticated_client, test_org, test_patient, test_provider, second_provider
    ):
        """Test that multiple SPECIALIST providers are allowed."""
        # Assign first provider as SPECIALIST
        response1 = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json={"provider_id": str(test_provider.id), "role": "SPECIALIST"}
        )
        assert response1.status_code == 201
        
        # Assign second provider as SPECIALIST
        response2 = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json={"provider_id": str(second_provider.id), "role": "SPECIALIST"}
        )
        assert response2.status_code == 201

    @pytest.mark.asyncio
    async def test_remove_from_care_team(
        self, authenticated_client, test_org, test_patient, test_provider
    ):
        """Test removing a provider from care team."""
        # Assign provider
        create_response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json={"provider_id": str(test_provider.id), "role": "SPECIALIST"}
        )
        assignment_id = create_response.json()["id"]
        
        # Remove
        response = await authenticated_client.delete(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team/{assignment_id}"
        )
        assert response.status_code == 204
        
        # Verify gone from list
        list_response = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team"
        )
        member_ids = [m["provider_id"] for m in list_response.json()["members"]]
        assert str(test_provider.id) not in member_ids

    @pytest.mark.asyncio
    async def test_duplicate_assignment_rejected(
        self, authenticated_client, test_org, test_patient, test_provider
    ):
        """Test that same provider cannot be assigned twice."""
        # First assignment
        await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json={"provider_id": str(test_provider.id), "role": "SPECIALIST"}
        )
        
        # Try duplicate
        response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/care-team",
            json={"provider_id": str(test_provider.id), "role": "CONSULTANT"}
        )
        assert response.status_code == 409
