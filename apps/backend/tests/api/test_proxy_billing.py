import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Import from src.models to match conftest
from src.models import Patient, Proxy, User

# Apply to all tests
pytestmark = pytest.mark.anyio


@pytest.fixture
async def test_patient(db_session: AsyncSession):
    """Create a dummy patient user and profile."""
    # Create user for patient
    user = User(
        email=f"patient_{uuid.uuid4()}@example.com",
        password_hash="dummy_hash",
        display_name="Test Patient",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create patient profile
    patient = Patient(
        user_id=user.id,
        first_name="Test",
        last_name="Patient",
        dob=date(1990, 1, 1),
        subscription_status="NONE",
        billing_manager_id=None,
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)

    return patient


@pytest.fixture
async def test_proxy(db_session: AsyncSession, test_user: User):
    """Create a proxy profile for the test user."""
    proxy = Proxy(user_id=test_user.id, relationship_to_patient="PARENT")
    db_session.add(proxy)
    await db_session.commit()
    await db_session.refresh(proxy)
    return proxy


async def test_list_managed_patient_subscriptions(
    client: AsyncClient,
    test_user: User,  # The proxy user
    test_proxy: Proxy,  # The proxy profile
    test_patient: Patient,  # The patient
    db_session: AsyncSession,
    test_user_token_headers: dict,
):
    """Test listing subscriptions for managed patients."""
    # 1. Assign test_user as billing manager for test_patient
    test_patient.billing_manager_id = test_user.id
    db_session.add(test_patient)
    await db_session.commit()

    # 2. Create active proxy relationship using message to bypass ORM issue
    # We use raw SQL because PatientProxyAssignment ORM in test env is flaky
    assignment_id = uuid.uuid4()
    await db_session.execute(
        text("""
            INSERT INTO patient_proxy_assignments (
                id, patient_id, proxy_id, relationship_type, 
                can_view_billing, can_view_profile, can_view_appointments,
                can_schedule_appointments, can_view_clinical_notes, can_message_providers,
                created_at, updated_at
            ) VALUES (
                :id, :patient_id, :proxy_id, 'PARENT', 
                true, true, true,
                false, false, false,
                now(), now()
            )
        """),
        {"id": assignment_id, "patient_id": test_patient.id, "proxy_id": test_proxy.id},
    )
    await db_session.commit()
    await db_session.commit()

    # 3. Call API
    response = await client.get("/api/v1/proxy/managed-patients/billing", headers=test_user_token_headers)
    assert response.status_code == 200, response.text
    data = response.json()

    # Depending on whether other tests ran, might be more than 1
    patient_ids = [d["patient_id"] for d in data]
    assert str(test_patient.id) in patient_ids

    patient_data = next(d for d in data if d["patient_id"] == str(test_patient.id))
    assert patient_data["subscription"]["status"] == "NONE"

    # Manual cleanup to avoid IntegrityError in teardown
    await db_session.execute(text("DELETE FROM patient_proxy_assignments WHERE id = :id"), {"id": assignment_id})
    await db_session.commit()


async def test_access_denied_without_billing_manager_assignment(
    client: AsyncClient,
    test_user: User,
    test_proxy: Proxy,
    test_patient: Patient,
    db_session: AsyncSession,
    test_user_token_headers: dict,
):
    """Test that patient doesn't show up if user is not billing manager."""
    # 1. Create active proxy relationship BUT DO NOT assign billing manager
    assignment_id = uuid.uuid4()
    await db_session.execute(
        text("""
            INSERT INTO patient_proxy_assignments (
                id, patient_id, proxy_id, relationship_type, 
                can_view_billing, can_view_profile, can_view_appointments,
                can_schedule_appointments, can_view_clinical_notes, can_message_providers,
                created_at, updated_at
            ) VALUES (
                :id, :patient_id, :proxy_id, 'PARENT', 
                true, true, true,
                false, false, false,
                now(), now()
            )
        """),
        {"id": assignment_id, "patient_id": test_patient.id, "proxy_id": test_proxy.id},
    )
    await db_session.commit()

    # 2. Call API
    response = await client.get("/api/v1/proxy/managed-patients/billing", headers=test_user_token_headers)
    assert response.status_code == 200
    data = response.json()

    patient_ids = [d["patient_id"] for d in data]
    assert str(test_patient.id) not in patient_ids

    # Manual cleanup
    await db_session.execute(text("DELETE FROM patient_proxy_assignments WHERE id = :id"), {"id": assignment_id})
    await db_session.commit()


async def test_create_managed_patient_checkout(
    client: AsyncClient,
    test_user: User,
    test_proxy: Proxy,
    test_patient: Patient,
    db_session: AsyncSession,
    test_user_token_headers: dict,
):
    """Test creating checkout session for managed patient."""
    # Setup billing manager & proxy relationship
    test_patient.billing_manager_id = test_user.id
    db_session.add(test_patient)
    await db_session.commit()

    assignment_id = uuid.uuid4()
    await db_session.execute(
        text("""
            INSERT INTO patient_proxy_assignments (
                id, patient_id, proxy_id, relationship_type, 
                can_view_billing, can_view_profile, can_view_appointments,
                can_schedule_appointments, can_view_clinical_notes, can_message_providers,
                created_at, updated_at
            ) VALUES (
                :id, :patient_id, :proxy_id, 'PARENT', 
                true, true, true,
                false, false, false,
                now(), now()
            )
        """),
        {"id": assignment_id, "patient_id": test_patient.id, "proxy_id": test_proxy.id},
    )
    await db_session.commit()

    # Mock Stripe
    with (
        patch("src.services.billing.create_customer", return_value="cus_test123"),
        patch(
            "src.services.billing.create_checkout_session",
            return_value=MagicMock(checkout_url="https://stripe.com/checkout", session_id="sess_123"),
        ),
    ):
        # Call API
        response = await client.post(
            f"/api/v1/proxy/managed-patients/{test_patient.id}/billing/checkout",
            json={"price_id": "price_123"},
            headers=test_user_token_headers,
        )

        assert response.status_code == 200
        assert response.json()["checkout_url"] == "https://stripe.com/checkout"

    # Manual cleanup
    await db_session.execute(text("DELETE FROM patient_proxy_assignments WHERE id = :id"), {"id": assignment_id})
    await db_session.commit()


async def test_create_managed_patient_checkout_unauthorized(
    client: AsyncClient,
    test_user: User,
    test_patient: Patient,
    db_session: AsyncSession,
    test_user_token_headers: dict,
):
    """Test 403 when trying to checkout for unmanaged patient."""
    # NO assignment

    response = await client.post(
        f"/api/v1/proxy/managed-patients/{test_patient.id}/billing/checkout",
        json={"price_id": "price_123"},
        headers=test_user_token_headers,
    )

    assert response.status_code == 403


async def test_cancel_managed_patient_subscription(
    client: AsyncClient,
    test_user: User,
    test_proxy: Proxy,
    test_patient: Patient,
    db_session: AsyncSession,
    test_user_token_headers: dict,
):
    """Test cancelling subscription for managed patient."""
    # Setup
    test_patient.billing_manager_id = test_user.id
    test_patient.stripe_customer_id = "cus_123"
    db_session.add(test_patient)
    await db_session.commit()

    assignment_id = uuid.uuid4()
    await db_session.execute(
        text("""
            INSERT INTO patient_proxy_assignments (
                id, patient_id, proxy_id, relationship_type, 
                can_view_billing, can_view_profile, can_view_appointments,
                can_schedule_appointments, can_view_clinical_notes, can_message_providers,
                created_at, updated_at
            ) VALUES (
                :id, :patient_id, :proxy_id, 'PARENT', 
                true, true, true,
                false, false, false,
                now(), now()
            )
        """),
        {"id": assignment_id, "patient_id": test_patient.id, "proxy_id": test_proxy.id},
    )
    await db_session.commit()

    # Mock Stripe
    with (
        patch("stripe.Subscription.list", return_value=MagicMock(data=[MagicMock(id="sub_123")])),
        patch(
            "stripe.Subscription.modify",
            return_value=MagicMock(id="sub_123", status="active", canceled_at=1234567890, cancel_at_period_end=True),
        ),
    ):
        # Call API
        response = await client.post(
            f"/api/v1/proxy/managed-patients/{test_patient.id}/billing/cancel",
            json={"cancel_immediately": False},
            headers=test_user_token_headers,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "active"
        assert response.json()["cancel_at_period_end"] is True

    # Manual cleanup
    await db_session.execute(text("DELETE FROM patient_proxy_assignments WHERE id = :id"), {"id": assignment_id})
    await db_session.commit()
