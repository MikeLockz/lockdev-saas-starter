from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models import Organization, OrganizationMember, OrganizationPatient, Patient, Provider, User
from src.models.assignments import PatientProxyAssignment
from src.models.profiles import Proxy
from src.security.auth import get_current_user


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as c:
        yield c


@pytest.fixture
async def test_user(db_session):
    unique_email = f"appt-test-{uuid4().hex[:8]}@example.com"
    user = User(email=unique_email, password_hash="hash", display_name="Appt Test User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_org(db_session, test_user):
    org = Organization(name="Appt Test Org", created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
    db_session.add(org)
    await db_session.flush()
    membership = OrganizationMember(
        organization_id=org.id,
        user_id=test_user.id,
        role="ADMIN",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def authenticated_client(client, test_user):
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides = {}


@pytest.fixture
async def test_provider(db_session, test_org):
    unique_email = f"provider-appt-{uuid4().hex[:8]}@example.com"
    user = User(email=unique_email, password_hash="hash", display_name="Dr. Appt")
    db_session.add(user)
    await db_session.flush()

    provider = Provider(
        organization_id=test_org.id,
        user_id=user.id,
        specialty="General",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(provider)
    await db_session.commit()
    await db_session.refresh(provider)
    return provider


@pytest.fixture
async def test_patient(db_session, test_org):
    patient = Patient(
        first_name="John",
        last_name="Doe",
        dob=date(1980, 1, 1),
        medical_record_number=f"MRN-{uuid4().hex[:6]}",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(patient)
    await db_session.flush()

    # Enroll
    enrollment = OrganizationPatient(
        organization_id=test_org.id, patient_id=patient.id, status="ACTIVE", enrolled_at=datetime.now(UTC)
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


class TestAppointmentAPI:
    @pytest.mark.asyncio
    async def test_create_appointment(self, authenticated_client, test_org, test_provider, test_patient):
        schedule_time = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        data = {
            "patient_id": str(test_patient.id),
            "provider_id": str(test_provider.id),
            "scheduled_at": schedule_time,
            "duration_minutes": 30,
            "reason": "Test Checkup",
        }
        res = await authenticated_client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
        assert res.status_code == 201, f"Failed to create appointment: {res.text}"
        assert res.json()["status"] == "SCHEDULED"

    @pytest.mark.asyncio
    async def test_double_booking_rejected(self, authenticated_client, test_org, test_provider, test_patient):
        # Create first
        schedule_time = (datetime.now(UTC) + timedelta(days=2)).isoformat()
        data = {
            "patient_id": str(test_patient.id),
            "provider_id": str(test_provider.id),
            "scheduled_at": schedule_time,
            "duration_minutes": 60,
            "reason": "First",
        }
        await authenticated_client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)

        # Try overlapping
        data["reason"] = "Second"
        res = await authenticated_client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
        assert res.status_code == 409

    @pytest.mark.asyncio
    async def test_list_appointments(self, authenticated_client, test_org, test_provider, test_patient):
        # Create one
        schedule_time = (datetime.now(UTC) + timedelta(hours=5)).isoformat()
        data = {
            "patient_id": str(test_patient.id),
            "provider_id": str(test_provider.id),
            "scheduled_at": schedule_time,
            "duration_minutes": 30,
            "reason": "List Test",
        }
        await authenticated_client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)

        # List with explicit date filter
        start = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        end = (datetime.now(UTC) + timedelta(days=2)).isoformat()
        res = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/appointments", params={"date_from": start, "date_to": end}
        )
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 1


class TestAppointmentAuthorization:
    """Test patient/proxy authorization for appointment scheduling."""

    @pytest.mark.asyncio
    async def test_patient_can_book_for_self(self, client, db_session, test_org, test_provider):
        """Patient should be able to schedule an appointment for themselves."""
        # Create a patient user
        patient_user = User(
            email=f"patient-{uuid4().hex[:8]}@example.com",
            password_hash="hash",
            display_name="Patient User",
        )
        db_session.add(patient_user)
        await db_session.flush()

        # Create patient profile linked to user
        patient = Patient(
            user_id=patient_user.id,
            first_name="Self",
            last_name="Booker",
            dob=date(1990, 5, 15),
            medical_record_number=f"MRN-{uuid4().hex[:6]}",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(patient)
        await db_session.flush()

        # Enroll patient in org
        enrollment = OrganizationPatient(
            organization_id=test_org.id, patient_id=patient.id, status="ACTIVE", enrolled_at=datetime.now(UTC)
        )
        db_session.add(enrollment)

        # Make patient a member of the org (required for access)
        membership = OrganizationMember(
            organization_id=test_org.id,
            user_id=patient_user.id,
            role="PATIENT",  # Patient role, not Staff/Admin
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(membership)
        await db_session.commit()

        # Override auth to be this patient user
        app.dependency_overrides[get_current_user] = lambda: patient_user

        try:
            schedule_time = (datetime.now(UTC) + timedelta(days=3)).isoformat()
            data = {
                "patient_id": str(patient.id),
                "provider_id": str(test_provider.id),
                "scheduled_at": schedule_time,
                "duration_minutes": 30,
                "reason": "Self booking",
            }
            res = await client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
            assert res.status_code == 201, f"Patient should be able to book for self: {res.text}"
        finally:
            app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_patient_cannot_book_for_another_patient(
        self, client, db_session, test_org, test_provider, test_patient
    ):
        """Patient should NOT be able to schedule for a different patient."""
        # Create a different patient user
        patient_user = User(
            email=f"patient2-{uuid4().hex[:8]}@example.com",
            password_hash="hash",
            display_name="Another Patient",
        )
        db_session.add(patient_user)
        await db_session.flush()

        # Create their own patient profile (different from test_patient)
        own_patient = Patient(
            user_id=patient_user.id,
            first_name="Own",
            last_name="Profile",
            dob=date(1985, 3, 20),
            medical_record_number=f"MRN-{uuid4().hex[:6]}",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(own_patient)
        await db_session.flush()

        # Enroll both patients
        enrollment = OrganizationPatient(
            organization_id=test_org.id, patient_id=own_patient.id, status="ACTIVE", enrolled_at=datetime.now(UTC)
        )
        db_session.add(enrollment)

        # Make patient a member
        membership = OrganizationMember(
            organization_id=test_org.id,
            user_id=patient_user.id,
            role="PATIENT",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(membership)
        await db_session.commit()

        # Override auth to be this patient user
        app.dependency_overrides[get_current_user] = lambda: patient_user

        try:
            schedule_time = (datetime.now(UTC) + timedelta(days=4)).isoformat()
            data = {
                "patient_id": str(test_patient.id),  # Trying to book for different patient!
                "provider_id": str(test_provider.id),
                "scheduled_at": schedule_time,
                "duration_minutes": 30,
                "reason": "Unauthorized booking attempt",
            }
            res = await client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
            assert res.status_code == 403, f"Patient should NOT book for others: {res.text}"
            assert "Not authorized" in res.json()["detail"]
        finally:
            app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_proxy_with_permission_can_book(self, client, db_session, test_org, test_provider, test_patient):
        """Proxy with can_schedule_appointments=True should be able to book for assigned patient."""
        # Create proxy user
        proxy_user = User(
            email=f"proxy-{uuid4().hex[:8]}@example.com",
            password_hash="hash",
            display_name="Proxy User",
        )
        db_session.add(proxy_user)
        await db_session.flush()

        # Create proxy profile
        proxy = Proxy(
            user_id=proxy_user.id,
            relationship_to_patient="PARENT",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(proxy)
        await db_session.flush()

        # Create assignment with scheduling permission
        assignment = PatientProxyAssignment(
            proxy_id=proxy.id,
            patient_id=test_patient.id,
            relationship_type="PARENT",
            can_schedule_appointments=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(assignment)

        # Make proxy a member
        membership = OrganizationMember(
            organization_id=test_org.id,
            user_id=proxy_user.id,
            role="PROXY",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(membership)
        await db_session.commit()

        app.dependency_overrides[get_current_user] = lambda: proxy_user

        try:
            schedule_time = (datetime.now(UTC) + timedelta(days=5)).isoformat()
            data = {
                "patient_id": str(test_patient.id),
                "provider_id": str(test_provider.id),
                "scheduled_at": schedule_time,
                "duration_minutes": 30,
                "reason": "Proxy booking",
            }
            res = await client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
            assert res.status_code == 201, f"Authorized proxy should book: {res.text}"
        finally:
            app.dependency_overrides = {}

    @pytest.mark.asyncio
    async def test_proxy_without_permission_cannot_book(
        self, client, db_session, test_org, test_provider, test_patient
    ):
        """Proxy with can_schedule_appointments=False should NOT be able to book."""
        # Create proxy user
        proxy_user = User(
            email=f"proxy-noperm-{uuid4().hex[:8]}@example.com",
            password_hash="hash",
            display_name="Proxy No Permission",
        )
        db_session.add(proxy_user)
        await db_session.flush()

        # Create proxy profile
        proxy = Proxy(
            user_id=proxy_user.id,
            relationship_to_patient="GUARDIAN",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(proxy)
        await db_session.flush()

        # Create assignment WITHOUT scheduling permission
        assignment = PatientProxyAssignment(
            proxy_id=proxy.id,
            patient_id=test_patient.id,
            relationship_type="GUARDIAN",
            can_schedule_appointments=False,  # No permission!
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(assignment)

        # Make proxy a member
        membership = OrganizationMember(
            organization_id=test_org.id,
            user_id=proxy_user.id,
            role="PROXY",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db_session.add(membership)
        await db_session.commit()

        app.dependency_overrides[get_current_user] = lambda: proxy_user

        try:
            schedule_time = (datetime.now(UTC) + timedelta(days=6)).isoformat()
            data = {
                "patient_id": str(test_patient.id),
                "provider_id": str(test_provider.id),
                "scheduled_at": schedule_time,
                "duration_minutes": 30,
                "reason": "Unauthorized proxy booking",
            }
            res = await client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
            assert res.status_code == 403, f"Proxy without permission should be denied: {res.text}"
        finally:
            app.dependency_overrides = {}
