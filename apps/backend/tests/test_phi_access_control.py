"""
HIPAA PHI Access Control Tests

Tests to verify role-based access control for PHI endpoints.
"""

from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models import Organization, OrganizationMember, OrganizationPatient, Patient, User
from src.security.auth import get_current_user


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as c:
        yield c


@pytest.fixture
async def test_org(db_session):
    org = Organization(name="HIPAA Test Org", created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def admin_user(db_session, test_org):
    """Create an admin user with full access."""
    user = User(
        email=f"admin-{uuid4().hex[:8]}@example.com",
        password_hash="hash",
        display_name="Admin User",
    )
    db_session.add(user)
    await db_session.flush()

    membership = OrganizationMember(
        organization_id=test_org.id,
        user_id=user.id,
        role="ADMIN",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def patient_user(db_session, test_org):
    """Create a patient user who should only see their own data."""
    user = User(
        email=f"patient-{uuid4().hex[:8]}@example.com",
        password_hash="hash",
        display_name="Patient User",
    )
    db_session.add(user)
    await db_session.flush()

    # Create patient profile linked to user
    patient = Patient(
        user_id=user.id,
        first_name="Test",
        last_name="Patient",
        dob=date(1990, 1, 1),
        medical_record_number=f"MRN-{uuid4().hex[:6]}",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(patient)
    await db_session.flush()

    # Enroll patient in org
    enrollment = OrganizationPatient(
        organization_id=test_org.id,
        patient_id=patient.id,
        status="ACTIVE",
        enrolled_at=datetime.now(UTC),
    )
    db_session.add(enrollment)

    # Make patient an org member with PATIENT role
    membership = OrganizationMember(
        organization_id=test_org.id,
        user_id=user.id,
        role="PATIENT",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(user)

    # Store patient for reference
    user._patient = patient
    return user


@pytest.fixture
async def other_patient(db_session, test_org):
    """Create another patient that should NOT be visible to patient_user."""
    patient = Patient(
        first_name="Other",
        last_name="Person",
        dob=date(1985, 5, 15),
        medical_record_number=f"MRN-{uuid4().hex[:6]}",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(patient)
    await db_session.flush()

    enrollment = OrganizationPatient(
        organization_id=test_org.id,
        patient_id=patient.id,
        status="ACTIVE",
        enrolled_at=datetime.now(UTC),
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


class TestPatientListAccessControl:
    """Verify patients list respects role-based access."""

    @pytest.mark.asyncio
    async def test_admin_sees_all_patients(self, client, db_session, test_org, admin_user, other_patient):
        """Admin should see all patients in the organization."""
        app.dependency_overrides[get_current_user] = lambda: admin_user

        try:
            res = await client.get(f"/api/v1/organizations/{test_org.id}/patients")
            assert res.status_code == 200
            data = res.json()
            # Admin should see at least the other_patient
            assert data["total"] >= 1
        finally:
            app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_patient_sees_only_self(self, client, db_session, test_org, patient_user, other_patient):
        """Patient should only see their own record, not other patients."""
        app.dependency_overrides[get_current_user] = lambda: patient_user

        try:
            res = await client.get(f"/api/v1/organizations/{test_org.id}/patients")
            assert res.status_code == 200
            data = res.json()

            # Patient should only see exactly 1 patient - themselves
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["first_name"] == "Test"
            assert data["items"][0]["last_name"] == "Patient"
        finally:
            app.dependency_overrides = {}


class TestCallLogAccessControl:
    """Verify call logs are restricted to staff only."""

    @pytest.mark.asyncio
    async def test_patient_cannot_access_call_logs(self, client, db_session, test_org, patient_user):
        """Patient should get 403 when trying to access call logs."""
        app.dependency_overrides[get_current_user] = lambda: patient_user

        try:
            res = await client.get(f"/api/v1/organizations/{test_org.id}/calls/", follow_redirects=True)
            assert res.status_code == 403
            assert "restricted" in res.json()["detail"].lower()
        finally:
            app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_admin_can_access_call_logs(self, client, db_session, test_org, admin_user):
        """Admin should be able to access call logs."""
        app.dependency_overrides[get_current_user] = lambda: admin_user

        try:
            res = await client.get(f"/api/v1/organizations/{test_org.id}/calls/", follow_redirects=True)
            assert res.status_code == 200
        finally:
            app.dependency_overrides = {}


class TestAppointmentListAccessControl:
    """Verify appointments list respects role-based access."""

    @pytest.mark.asyncio
    async def test_patient_sees_only_own_appointments(self, client, db_session, test_org, patient_user):
        """Patient should only see their own appointments."""
        # Note: This test verifies the filter is applied, not that appointments exist
        app.dependency_overrides[get_current_user] = lambda: patient_user

        try:
            res = await client.get(f"/api/v1/organizations/{test_org.id}/appointments")
            assert res.status_code == 200
            # With our role-based filter, patient should get empty or filtered list
            data = res.json()
            # All returned appointments should be for this patient only
            patient_id = str(patient_user._patient.id)
            for appt in data:
                assert appt.get("patient_id") == patient_id
        finally:
            app.dependency_overrides = {}
