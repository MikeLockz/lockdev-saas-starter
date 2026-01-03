"""Tests for Proxy API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime, timezone
from src.main import app
from src.models import User, Organization, OrganizationMember
from src.models.profiles import Patient, Proxy
from src.models.organizations import OrganizationPatient
from src.models.assignments import PatientProxyAssignment
from src.security.auth import get_current_user


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as c:
        yield c


@pytest.fixture
async def test_user(db_session):
    """Create a test admin user."""
    unique_email = f"proxy-admin-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Proxy Admin",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def proxy_user(db_session):
    """Create a user to be assigned as proxy."""
    unique_email = f"proxy-user-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Proxy User",
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
        name="Proxy Test Practice",
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
async def authenticated_client(client, test_user):
    """Client authenticated as test admin."""
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides = {}


class TestProxyAPI:
    """Test Proxy API endpoints."""

    @pytest.mark.asyncio
    async def test_assign_proxy(
        self, authenticated_client, test_org, test_patient, proxy_user
    ):
        """Test assigning a proxy to a patient."""
        data = {
            "email": proxy_user.email,
            "relationship_type": "PARENT",
            "permissions": {
                "can_view_profile": True,
                "can_view_appointments": True,
                "can_schedule_appointments": True,
                "can_view_clinical_notes": False,
                "can_view_billing": True,
                "can_message_providers": False
            }
        }
        response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies",
            json=data
        )
        assert response.status_code == 201, f"Response: {response.text}"
        
        result = response.json()
        assert result["relationship_type"] == "PARENT"
        assert result["can_schedule_appointments"] is True
        assert result["can_view_clinical_notes"] is False
        assert result["user"]["email"] == proxy_user.email

    @pytest.mark.asyncio
    async def test_list_patient_proxies(
        self, authenticated_client, test_org, test_patient, proxy_user
    ):
        """Test listing proxies for a patient."""
        # First assign proxy
        await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies",
            json={"email": proxy_user.email, "relationship_type": "SPOUSE"}
        )
        
        # List proxies
        response = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["patient_id"] == str(test_patient.id)
        assert len(result["proxies"]) >= 1

    @pytest.mark.asyncio
    async def test_update_proxy_permissions(
        self, authenticated_client, test_org, test_patient, proxy_user
    ):
        """Test updating proxy permissions."""
        # Assign proxy
        create_response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies",
            json={"email": proxy_user.email, "relationship_type": "GUARDIAN"}
        )
        assignment_id = create_response.json()["id"]
        
        # Update permissions
        response = await authenticated_client.patch(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies/{assignment_id}",
            json={
                "permissions": {
                    "can_view_clinical_notes": True,
                    "can_message_providers": True
                }
            }
        )
        assert response.status_code == 200, f"Response: {response.text}"
        
        result = response.json()
        assert result["can_view_clinical_notes"] is True
        assert result["can_message_providers"] is True

    @pytest.mark.asyncio
    async def test_revoke_proxy(
        self, authenticated_client, test_org, test_patient, proxy_user
    ):
        """Test revoking proxy access."""
        # Assign proxy
        create_response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies",
            json={"email": proxy_user.email, "relationship_type": "CAREGIVER"}
        )
        assignment_id = create_response.json()["id"]
        
        # Revoke
        response = await authenticated_client.delete(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies/{assignment_id}"
        )
        assert response.status_code == 204
        
        # Verify no longer in list
        list_response = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies"
        )
        proxy_ids = [p["id"] for p in list_response.json()["proxies"]]
        assert assignment_id not in proxy_ids

    @pytest.mark.asyncio
    async def test_duplicate_proxy_rejected(
        self, authenticated_client, test_org, test_patient, proxy_user
    ):
        """Test that same user cannot be assigned as proxy twice."""
        # First assignment
        await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies",
            json={"email": proxy_user.email, "relationship_type": "PARENT"}
        )
        
        # Try duplicate
        response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies",
            json={"email": proxy_user.email, "relationship_type": "GUARDIAN"}
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_proxy_not_found_user(
        self, authenticated_client, test_org, test_patient
    ):
        """Test assigning proxy with non-existent email."""
        response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/patients/{test_patient.id}/proxies",
            json={"email": "nonexistent@example.com", "relationship_type": "PARENT"}
        )
        assert response.status_code == 404
        assert "User not found" in response.text


class TestProxyDashboard:
    """Test proxy dashboard endpoint."""

    @pytest.mark.asyncio
    async def test_my_proxy_patients(
        self, client, db_session, test_org, test_patient, proxy_user
    ):
        """Test the proxy dashboard endpoint."""
        now = datetime.now(timezone.utc)
        
        # Create proxy profile
        proxy = Proxy(
            user_id=proxy_user.id,
            relationship_to_patient="PARENT",
            created_at=now,
            updated_at=now,
        )
        db_session.add(proxy)
        await db_session.flush()
        
        # Create assignment
        assignment = PatientProxyAssignment(
            proxy_id=proxy.id,
            patient_id=test_patient.id,
            relationship_type="PARENT",
            can_view_profile=True,
            can_view_appointments=True,
            granted_at=now,
            created_at=now,
            updated_at=now,
        )
        db_session.add(assignment)
        await db_session.commit()
        
        # Auth as proxy user
        app.dependency_overrides[get_current_user] = lambda: proxy_user
        
        try:
            response = await client.get("/api/v1/users/me/proxy-patients")
            assert response.status_code == 200
            
            result = response.json()
            assert len(result) >= 1
            assert result[0]["patient"]["first_name"] == "Test"
            assert result[0]["relationship_type"] == "PARENT"
        finally:
            app.dependency_overrides = {}
