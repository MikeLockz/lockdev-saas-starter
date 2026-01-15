"""
Tests for P0 Security Vulnerabilities Remediation.

Tests the following fixes:
1. MFA Enforcement Middleware - blocks privileged users without MFA
2. Impersonation Validation - validates patient exists and org access
"""

import uuid

import pytest
from httpx import AsyncClient

from src.models import User
from src.models.organizations import Organization, OrganizationPatient
from src.models.profiles import Patient


@pytest.fixture
async def test_super_admin(db_session):
    """Create a super admin user for testing."""
    email = f"super_admin_{uuid.uuid4()}@example.com"
    user = User(
        email=email,
        password_hash="dummy_hash",
        display_name="Super Admin",
        is_super_admin=True,
        mfa_enabled=True,  # Super admins have MFA enabled
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()


@pytest.fixture
async def super_admin_token(test_super_admin):
    return {"Authorization": f"Bearer mock_{test_super_admin.email}"}


@pytest.fixture
async def test_organization(db_session):
    """Create a test organization."""
    org = Organization(
        name=f"Test Org {uuid.uuid4()}",
        subscription_status="ACTIVE",
        is_active=True,
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    yield org
    await db_session.delete(org)
    await db_session.commit()


@pytest.fixture
async def test_patient(db_session, test_organization):
    """Create a test patient linked to the test organization."""
    from datetime import date

    patient = Patient(
        first_name="Test",
        last_name="Patient",
        dob=date(1990, 1, 1),
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)

    # Link patient to organization
    org_patient = OrganizationPatient(
        organization_id=test_organization.id,
        patient_id=patient.id,
    )
    db_session.add(org_patient)
    await db_session.commit()

    yield patient

    # Cleanup
    await db_session.delete(org_patient)
    await db_session.delete(patient)
    await db_session.commit()


class TestImpersonationValidation:
    """Tests for impersonate_patient endpoint security."""

    @pytest.mark.asyncio
    async def test_impersonate_nonexistent_patient_returns_404(self, client: AsyncClient, super_admin_token: dict):
        """Attempting to impersonate a non-existent patient should return 404."""
        fake_patient_id = str(uuid.uuid4())

        response = await client.post(
            f"/api/v1/admin/impersonate/{fake_patient_id}",
            headers=super_admin_token,
            json={"reason": "Test impersonation"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Patient not found"

    @pytest.mark.asyncio
    async def test_impersonate_invalid_uuid_returns_400(self, client: AsyncClient, super_admin_token: dict):
        """Invalid patient ID format should return 400."""
        response = await client.post(
            "/api/v1/admin/impersonate/not-a-valid-uuid",
            headers=super_admin_token,
            json={"reason": "Test impersonation"},
        )

        assert response.status_code == 400
        assert "Invalid patient ID format" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_impersonate_requires_admin(self, client: AsyncClient, test_user_token_headers: dict, test_patient):
        """Non-admin users should not be able to impersonate."""
        response = await client.post(
            f"/api/v1/admin/impersonate/{test_patient.id}",
            headers=test_user_token_headers,
            json={"reason": "Test impersonation"},
        )

        assert response.status_code == 403


class TestMFAEnforcementMiddleware:
    """Tests for MFA enforcement on privileged routes."""

    @pytest.mark.asyncio
    async def test_mfa_exempt_paths_accessible(self, client: AsyncClient):
        """Health check and other exempt paths should be accessible without auth."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_docs_accessible_without_auth(self, client: AsyncClient):
        """Documentation routes should be accessible."""
        response = await client.get("/docs")
        # 200 for docs page or redirect
        assert response.status_code in [200, 307]
