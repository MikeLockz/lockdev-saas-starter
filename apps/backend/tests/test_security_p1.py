import asyncio
import uuid
from datetime import UTC, date, datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from src.models import Organization, OrganizationMember, OrganizationPatient, Patient, Provider, User


@pytest.fixture
async def setup_org(db_session):
    # Create Org
    unique = uuid.uuid4().hex[:8]
    org = Organization(name=f"P1 Test Org {unique}", is_active=True)
    db_session.add(org)
    await db_session.flush()

    # Create Super Admin
    admin_user = User(
        email=f"super_admin_{unique}@example.com",
        password_hash="hash",
        display_name="Super Admin",
        is_super_admin=True,
        mfa_enabled=True,
    )
    db_session.add(admin_user)

    # Create Provider User
    provider_user = User(email=f"provider_{unique}@example.com", password_hash="hash", display_name="Dr. Test")
    db_session.add(provider_user)
    await db_session.flush()

    # Create Provider Profile
    provider = Provider(organization_id=org.id, user_id=provider_user.id, specialty="General")
    db_session.add(provider)
    await db_session.flush()

    # Create Patient User & Profile
    patient_user = User(email=f"patient_{unique}@example.com", password_hash="hash", display_name="Patient Test")
    db_session.add(patient_user)
    await db_session.flush()

    patient = Patient(
        user_id=patient_user.id,
        first_name="Test",
        last_name="Patient",
        dob=date(1990, 1, 1),
        medical_record_number=f"MRN-{unique}",
    )
    db_session.add(patient)
    await db_session.flush()

    # Enroll Patient
    enrollment = OrganizationPatient(organization_id=org.id, patient_id=patient.id, status="ACTIVE")
    db_session.add(enrollment)

    # Admin Membership (for test setup if needed, though super admin has access)
    # But for creating appointments, we need a user in the org.
    # Let's verify who is creating the appointment.
    # Race condition test usually impersonates a scheduler (Staff/Admin/Provider).
    staff_user = User(
        email=f"staff_{unique}@example.com",
        password_hash="hash",
        display_name="Staff Scheduler",
        mfa_enabled=True,
    )
    db_session.add(staff_user)
    await db_session.flush()

    staff_member = OrganizationMember(organization_id=org.id, user_id=staff_user.id, role="STAFF")
    db_session.add(staff_member)

    await db_session.commit()

    return {
        "org": org,
        "super_admin": admin_user,
        "provider": provider,
        "patient": patient,
        "staff_user": staff_user,
        "patient_user": patient_user,
    }


@pytest.mark.asyncio
async def test_impersonation_security(client: AsyncClient, setup_org, db_session):
    """
    Verify that impersonation strictly validates existence of the patient profile.
    P1 Issue: Privilege Escalation Risk if User IDs can be spoofed as Patient IDs.
    """
    data = setup_org
    super_admin = data["super_admin"]
    patient = data["patient"]

    headers = {"Authorization": f"Bearer mock_{super_admin.email}"}

    # Mock Firebase Auth to avoid actual calls (and errors)
    with patch("firebase_admin.auth.create_custom_token") as mock_token:
        mock_token.return_value = b"mock-custom-token"

        # 1. Test Valid Impersonation
        res = await client.post(f"/api/v1/admin/impersonate/{patient.id}", json={"reason": "Support"}, headers=headers)
        assert res.status_code == 200
        assert res.json()["token"] == "mock-custom-token"

        # 2. Test Impersonation of Non-Existent UUID
        random_uuid = uuid.uuid4()
        res = await client.post(f"/api/v1/admin/impersonate/{random_uuid}", json={"reason": "Attack"}, headers=headers)
        assert res.status_code == 404
        assert "Patient not found" in res.json()["detail"]

        # 3. Test Impersonation of User ID (Lateral Movement Attempt)
        # Attempt to impersonate the Super Admin themselves (using their User ID)
        # Since User ID != Patient ID, and check is against Patient table, this MUST fail (404).
        res = await client.post(
            f"/api/v1/admin/impersonate/{super_admin.id}", json={"reason": "Lateral Move"}, headers=headers
        )
        assert res.status_code == 404
        assert "Patient not found" in res.json()["detail"]


@pytest.mark.asyncio
async def test_appointment_race_condition(client: AsyncClient, setup_org):
    """
    Verify that row locking prevents double booking.
    """
    data = setup_org
    staff_user = data["staff_user"]
    org = data["org"]
    provider = data["provider"]
    patient = data["patient"]

    headers = {"Authorization": f"Bearer mock_{staff_user.email}"}

    schedule_time = (datetime.now(UTC) + timedelta(days=5)).isoformat()

    payload = {
        "patient_id": str(patient.id),
        "provider_id": str(provider.id),
        "scheduled_at": schedule_time,
        "duration_minutes": 30,
        "reason": "Race Test",
    }

    # We need to simulate concurrent requests.
    # Since we are using an async client, we can fire two requests "simultaneously" using gather.
    # The database locking should cause them to serialize at the DB level.
    # One should succeed (201), one should fail (409 Conflict) because of the double-booking check logic
    # that runs AFTER the lock is acquired.

    # Note: `with_for_update` serializes execution.
    # 1. T1 acquires lock, checks overlap (none), inserts, commits (release lock).
    # 2. T2 waits... gets lock, checking overlap (found T1's apt), returns 409.

    async def create_appt(reason_suffix):
        p = payload.copy()
        p["reason"] += reason_suffix
        return await client.post(f"/api/v1/organizations/{org.id}/appointments", json=p, headers=headers)

    # Use asyncio.gather to run concurrently
    results = await asyncio.gather(create_appt(" A"), create_appt(" B"))

    # Check results
    status_codes = [r.status_code for r in results]
    assert 201 in status_codes
    assert 409 in status_codes
    assert status_codes.count(201) == 1
    assert status_codes.count(409) == 1
