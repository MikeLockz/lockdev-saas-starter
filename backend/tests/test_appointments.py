import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime, timezone, timedelta, date
from src.main import app
from src.models import User, Organization, OrganizationMember, Provider, Patient, OrganizationPatient
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
    org = Organization(name="Appt Test Org", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    db_session.add(org)
    await db_session.flush()
    membership = OrganizationMember(organization_id=org.id, user_id=test_user.id, role="ADMIN", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
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
    
    provider = Provider(organization_id=test_org.id, user_id=user.id, specialty="General", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    db_session.add(provider)
    await db_session.commit()
    await db_session.refresh(provider)
    return provider

@pytest.fixture
async def test_patient(db_session, test_org):
    patient = Patient(first_name="John", last_name="Doe", dob=date(1980, 1, 1), medical_record_number=f"MRN-{uuid4().hex[:6]}", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    db_session.add(patient)
    await db_session.flush()
    
    # Enroll
    enrollment = OrganizationPatient(organization_id=test_org.id, patient_id=patient.id, status="ACTIVE", enrolled_at=datetime.now(timezone.utc))
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient

class TestAppointmentAPI:
    @pytest.mark.asyncio
    async def test_create_appointment(self, authenticated_client, test_org, test_provider, test_patient):
        schedule_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        data = {
            "patient_id": str(test_patient.id),
            "provider_id": str(test_provider.id),
            "scheduled_at": schedule_time,
            "duration_minutes": 30,
            "reason": "Test Checkup"
        }
        res = await authenticated_client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
        assert res.status_code == 201, f"Failed to create appointment: {res.text}"
        assert res.json()["status"] == "SCHEDULED"

    @pytest.mark.asyncio
    async def test_double_booking_rejected(self, authenticated_client, test_org, test_provider, test_patient):
        # Create first
        schedule_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        data = {
            "patient_id": str(test_patient.id),
            "provider_id": str(test_provider.id),
            "scheduled_at": schedule_time,
            "duration_minutes": 60,
            "reason": "First"
        }
        await authenticated_client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
        
        # Try overlapping
        data["reason"] = "Second"
        res = await authenticated_client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
        assert res.status_code == 409

    @pytest.mark.asyncio
    async def test_list_appointments(self, authenticated_client, test_org, test_provider, test_patient):
         # Create one
        schedule_time = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
        data = {
            "patient_id": str(test_patient.id),
            "provider_id": str(test_provider.id),
            "scheduled_at": schedule_time,
            "duration_minutes": 30,
            "reason": "List Test"
        }
        await authenticated_client.post(f"/api/v1/organizations/{test_org.id}/appointments", json=data)
        
        # List with explicit date filter
        start = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        res = await authenticated_client.get(
            f"/api/v1/organizations/{test_org.id}/appointments", 
            params={"date_from": start, "date_to": end}
        )
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 1
