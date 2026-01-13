"""
Admin Billing API Tests

Tests for Story 22.4 - Admin Billing Management API
"""

import uuid
from datetime import date, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.billing import BillingTransaction, SubscriptionOverride
from src.models.profiles import Patient
from src.models.users import User


@pytest.fixture
async def db(db_session):
    return db_session


@pytest.fixture
async def super_admin_user(db: AsyncSession):
    """Create a super admin user."""
    user = User(
        email=f"superadmin_{uuid.uuid4()}@example.com",
        password_hash="hash",
        display_name="Super Admin",
        is_super_admin=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def super_admin_auth_headers(super_admin_user):
    return {"Authorization": f"Bearer mock_{super_admin_user.email}"}


@pytest.fixture
async def regular_user(db: AsyncSession):
    """Create a regular (non-admin) user."""
    user = User(
        email=f"regular_{uuid.uuid4()}@example.com",
        password_hash="hash",
        display_name="Regular User",
        is_super_admin=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def regular_user_auth_headers(regular_user):
    return {"Authorization": f"Bearer mock_{regular_user.email}"}


@pytest.fixture
async def patient_with_subscription(db: AsyncSession, regular_user):
    """Create a patient with a Stripe subscription."""
    patient = Patient(
        user_id=regular_user.id,
        first_name="Test",
        last_name="Patient",
        dob=date(1990, 1, 1),
        subscription_status="ACTIVE",
        stripe_customer_id=f"cus_test_{uuid.uuid4().hex[:8]}",
        billing_manager_id=None,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@pytest.fixture
async def billing_transaction(db: AsyncSession, patient_with_subscription):
    """Create a billing transaction."""
    transaction = BillingTransaction(
        owner_id=patient_with_subscription.id,
        owner_type="PATIENT",
        stripe_payment_intent_id=f"pi_test_{uuid.uuid4().hex[:8]}",
        stripe_invoice_id=f"in_test_{uuid.uuid4().hex[:8]}",
        amount_cents=2999,
        currency="usd",
        status="SUCCEEDED",
        description="Subscription payment",
        receipt_number=f"REC-{uuid.uuid4().hex[:8]}",
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


@pytest.fixture
async def proxy_user(db: AsyncSession):
    """Create a proxy user for billing manager tests."""
    user = User(
        email=f"proxy_{uuid.uuid4()}@example.com",
        password_hash="hash",
        display_name="Proxy User",
        is_super_admin=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# =============================================================================
# Access Control Tests
# =============================================================================


@pytest.mark.asyncio
async def test_admin_billing_requires_super_admin(
    client: AsyncClient,
    regular_user_auth_headers: dict,
):
    """Test that non-admin users get 403 on admin billing endpoints."""
    response = await client.get(
        "/api/v1/admin/billing/subscriptions",
        headers=regular_user_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_billing_allowed_for_super_admin(
    client: AsyncClient,
    super_admin_auth_headers: dict,
):
    """Test that super admins can access admin billing endpoints."""
    response = await client.get(
        "/api/v1/admin/billing/subscriptions",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200


# =============================================================================
# Subscription List Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_subscriptions_empty(
    client: AsyncClient,
    super_admin_auth_headers: dict,
):
    """Test listing subscriptions when none exist."""
    response = await client.get(
        "/api/v1/admin/billing/subscriptions",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "subscriptions" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


@pytest.mark.asyncio
async def test_list_subscriptions_with_data(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    patient_with_subscription: Patient,
):
    """Test listing subscriptions with existing data."""
    response = await client.get(
        "/api/v1/admin/billing/subscriptions",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

    # Find our patient
    found = any(
        str(sub["owner_id"]) == str(patient_with_subscription.id)
        for sub in data["subscriptions"]
    )
    assert found


@pytest.mark.asyncio
async def test_list_subscriptions_with_filters(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    patient_with_subscription: Patient,
):
    """Test listing subscriptions with filters."""
    # Filter by status
    response = await client.get(
        "/api/v1/admin/billing/subscriptions?status=ACTIVE",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200

    # Filter by owner_type
    response = await client.get(
        "/api/v1/admin/billing/subscriptions?owner_type=PATIENT",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200

    # Search by name
    response = await client.get(
        "/api/v1/admin/billing/subscriptions?search=Test",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200


# =============================================================================
# Transaction List Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_transactions(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    billing_transaction: BillingTransaction,
):
    """Test listing all transactions."""
    response = await client.get(
        "/api/v1/admin/billing/transactions",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_transactions_with_status_filter(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    billing_transaction: BillingTransaction,
):
    """Test listing transactions with status filter."""
    response = await client.get(
        "/api/v1/admin/billing/transactions?status=SUCCEEDED",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    # All returned transactions should be SUCCEEDED
    for tx in data["transactions"]:
        assert tx["status"] == "SUCCEEDED"


# =============================================================================
# Analytics Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_billing_analytics(
    client: AsyncClient,
    super_admin_auth_headers: dict,
):
    """Test getting billing analytics."""
    response = await client.get(
        "/api/v1/admin/billing/analytics",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_active_subscriptions" in data
    assert "total_mrr_cents" in data
    assert "new_subscriptions_this_month" in data
    assert "cancelled_subscriptions_this_month" in data
    assert "churn_rate" in data
    assert "average_revenue_per_user_cents" in data
    assert "failed_payments_this_month" in data
    assert "total_revenue_this_month_cents" in data


# =============================================================================
# Grant Free Subscription Tests
# =============================================================================


@pytest.mark.asyncio
async def test_grant_free_subscription(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    patient_with_subscription: Patient,
):
    """Test granting a free subscription."""
    response = await client.post(
        "/api/v1/admin/billing/grant-free",
        headers=super_admin_auth_headers,
        json={
            "owner_id": str(patient_with_subscription.id),
            "owner_type": "PATIENT",
            "reason": "Testing free subscription grant",
            "duration_months": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["override_type"] == "FREE"
    assert data["owner_id"] == str(patient_with_subscription.id)


@pytest.mark.asyncio
async def test_grant_free_subscription_requires_reason(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    patient_with_subscription: Patient,
):
    """Test that granting free subscription requires a reason."""
    response = await client.post(
        "/api/v1/admin/billing/grant-free",
        headers=super_admin_auth_headers,
        json={
            "owner_id": str(patient_with_subscription.id),
            "owner_type": "PATIENT",
            "reason": "Short",  # Too short
        },
    )
    assert response.status_code == 422  # Validation error


# =============================================================================
# Billing Manager Management Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_billing_managers_empty(
    client: AsyncClient,
    super_admin_auth_headers: dict,
):
    """Test listing billing managers when none exist."""
    response = await client.get(
        "/api/v1/admin/billing/managers",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "relationships" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_admin_assign_billing_manager(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    patient_with_subscription: Patient,
    proxy_user: User,
):
    """Test admin assigning a billing manager."""
    response = await client.put(
        f"/api/v1/admin/patients/{patient_with_subscription.id}/billing/manager",
        headers=super_admin_auth_headers,
        json={"proxy_user_id": str(proxy_user.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "assigned by admin" in data["message"].lower()


@pytest.mark.asyncio
async def test_admin_assign_billing_manager_patient_not_found(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    proxy_user: User,
):
    """Test assigning billing manager to non-existent patient."""
    response = await client.put(
        f"/api/v1/admin/patients/{uuid.uuid4()}/billing/manager",
        headers=super_admin_auth_headers,
        json={"proxy_user_id": str(proxy_user.id)},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_remove_billing_manager(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    patient_with_subscription: Patient,
    proxy_user: User,
    db: AsyncSession,
):
    """Test admin removing a billing manager."""
    # First assign a billing manager
    patient_with_subscription.billing_manager_id = proxy_user.id
    patient_with_subscription.billing_manager_assigned_at = datetime.utcnow()
    await db.commit()

    # Now remove
    response = await client.delete(
        f"/api/v1/admin/patients/{patient_with_subscription.id}/billing/manager",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_admin_remove_billing_manager_not_assigned(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    patient_with_subscription: Patient,
):
    """Test removing billing manager when none is assigned."""
    response = await client.delete(
        f"/api/v1/admin/patients/{patient_with_subscription.id}/billing/manager",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 400


# =============================================================================
# Billing Manager List with Assignment Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_billing_managers_with_data(
    client: AsyncClient,
    super_admin_auth_headers: dict,
    patient_with_subscription: Patient,
    proxy_user: User,
    db: AsyncSession,
):
    """Test listing billing managers when assignments exist."""
    # Assign billing manager
    patient_with_subscription.billing_manager_id = proxy_user.id
    patient_with_subscription.billing_manager_assigned_at = datetime.utcnow()
    await db.commit()

    response = await client.get(
        "/api/v1/admin/billing/managers",
        headers=super_admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

    # Find our assignment
    found = any(
        str(rel["patient_id"]) == str(patient_with_subscription.id)
        and str(rel["billing_manager_id"]) == str(proxy_user.id)
        for rel in data["relationships"]
    )
    assert found
