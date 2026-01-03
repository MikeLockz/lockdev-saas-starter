"""Tests for Provider and Staff API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from src.main import app
from src.models import User, Organization, OrganizationMember
from src.security.auth import get_current_user


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as c:
        yield c


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    unique_email = f"provider-test-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Provider Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def provider_user(db_session):
    """Create a second user to be promoted to provider."""
    unique_email = f"provider-user-{uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        password_hash="hash",
        display_name="Dr. John Smith",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_org(db_session, test_user):
    """Create a test organization with the test user as admin."""
    from datetime import datetime, timezone
    
    org = Organization(
        name="Test Practice",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(org)
    await db_session.flush()
    
    membership = OrganizationMember(
        organization_id=org.id,
        user_id=test_user.id,
        role="ADMIN",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def authenticated_client(client, test_user):
    """Client authenticated as test_user."""
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides = {}


class TestProviderAPI:
    """Test Provider API endpoints."""

    @pytest.mark.asyncio
    async def test_create_provider_with_valid_npi(
        self, authenticated_client, test_org, provider_user, db_session
    ):
        """Test creating a provider with valid NPI."""
        data = {
            "user_id": str(provider_user.id),
            "npi_number": "1234567893",  # Valid NPI
            "specialty": "Internal Medicine",
            "license_number": "MD12345",
            "license_state": "CA",
        }
        response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/providers",
            json=data
        )
        assert response.status_code == 201, f"Response: {response.text}"
        
        result = response.json()
        assert result["npi_number"] == "1234567893"
        assert result["specialty"] == "Internal Medicine"
        assert result["is_active"] is True
        assert result["user_display_name"] == "Dr. John Smith"

    @pytest.mark.asyncio
    async def test_create_provider_invalid_npi_rejected(
        self, authenticated_client, test_org, provider_user
    ):
        """Test that invalid NPI is rejected with 422."""
        data = {
            "user_id": str(provider_user.id),
            "npi_number": "1234567890",  # Invalid checksum
            "specialty": "Cardiology",
        }
        response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/providers",
            json=data
        )
        assert response.status_code == 422, f"Response: {response.text}"
        assert "NPI" in response.text

    @pytest.mark.asyncio
    async def test_duplicate_npi_rejected(
        self, authenticated_client, test_org, provider_user, db_session
    ):
        """Test that duplicate NPI in same org is rejected."""
        # Create first provider
        data1 = {
            "user_id": str(provider_user.id),
            "npi_number": "1234567893",
            "specialty": "Internal Medicine",
        }
        response1 = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/providers",
            json=data1
        )
        assert response1.status_code == 201
        
        # Create second user
        second_user = User(
            email=f"second-provider-{uuid4().hex[:8]}@example.com",
            password_hash="hash",
            display_name="Dr. Jane Doe",
        )
        db_session.add(second_user)
        await db_session.commit()
        await db_session.refresh(second_user)
        
        # Try to create second provider with same NPI
        data2 = {
            "user_id": str(second_user.id),
            "npi_number": "1234567893",  # Same NPI
            "specialty": "Cardiology",
        }
        response2 = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/providers",
            json=data2
        )
        assert response2.status_code == 409, f"Response: {response2.text}"
        assert "NPI" in response2.text

    @pytest.mark.asyncio
    async def test_list_providers(
        self, authenticated_client, test_org, provider_user
    ):
        """Test listing providers."""
        # Create a provider first
        data = {
            "user_id": str(provider_user.id),
            "npi_number": "1234567893",
            "specialty": "Internal Medicine",
        }
        await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/providers",
            json=data
        )
        
        # List providers
        response = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/providers"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "items" in result
        assert "total" in result
        assert result["total"] >= 1

    @pytest.mark.asyncio
    async def test_update_provider(
        self, authenticated_client, test_org, provider_user
    ):
        """Test updating a provider."""
        # Create provider
        data = {
            "user_id": str(provider_user.id),
            "specialty": "Internal Medicine",
        }
        create_response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/providers",
            json=data
        )
        provider_id = create_response.json()["id"]
        
        # Update
        update_data = {"specialty": "Cardiology"}
        response = await authenticated_client.patch(
            f"/api/v1/organizations/{test_org.id}/providers/{provider_id}",
            json=update_data
        )
        assert response.status_code == 200
        assert response.json()["specialty"] == "Cardiology"

    @pytest.mark.asyncio
    async def test_delete_provider(
        self, authenticated_client, test_org, provider_user
    ):
        """Test soft deleting a provider."""
        # Create provider
        data = {
            "user_id": str(provider_user.id),
            "specialty": "Internal Medicine",
        }
        create_response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/providers",
            json=data
        )
        provider_id = create_response.json()["id"]
        
        # Delete
        response = await authenticated_client.delete(
            f"/api/v1/organizations/{test_org.id}/providers/{provider_id}"
        )
        assert response.status_code == 204
        
        # Verify not in list
        list_response = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/providers"
        )
        provider_ids = [p["id"] for p in list_response.json()["items"]]
        assert provider_id not in provider_ids


class TestStaffAPI:
    """Test Staff API endpoints."""

    @pytest.mark.asyncio
    async def test_create_staff(
        self, authenticated_client, test_org, provider_user
    ):
        """Test creating a staff member."""
        data = {
            "user_id": str(provider_user.id),
            "job_title": "Medical Assistant",
            "department": "Primary Care",
            "employee_id": "EMP001",
        }
        response = await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/staff",
            json=data
        )
        assert response.status_code == 201, f"Response: {response.text}"
        
        result = response.json()
        assert result["job_title"] == "Medical Assistant"
        assert result["department"] == "Primary Care"
        assert result["is_active"] is True

    @pytest.mark.asyncio
    async def test_list_staff(
        self, authenticated_client, test_org, provider_user
    ):
        """Test listing staff."""
        # Create staff first
        data = {
            "user_id": str(provider_user.id),
            "job_title": "Medical Assistant",
            "department": "Primary Care",
        }
        await authenticated_client.post(
            f"/api/v1/organizations/{test_org.id}/staff",
            json=data
        )
        
        # List staff
        response = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/staff"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "items" in result
        assert result["total"] >= 1
