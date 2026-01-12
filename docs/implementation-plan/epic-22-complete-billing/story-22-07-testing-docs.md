# Story 22.7: Testing & Documentation
**User Story:** As a Developer, I want comprehensive test coverage and documentation for the billing system, so that the code is maintainable and reliable.

## Status
- [ ] **Pending**

## Context
- **Epic:** Epic 22 - Complete Billing & Subscription Management
- **Dependencies:** All previous stories (22.1 - 22.6)

## Technical Specification
**Goal:** Achieve >90% test coverage for billing code and create comprehensive documentation.

### Changes Required

#### 1. Unit Tests: Backend

**`tests/services/test_billing_service.py`:**
```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.billing import (
    create_customer,
    create_checkout_session,
    cancel_subscription,
    refund_transaction,
    grant_free_subscription,
    get_subscription_status,
)

@pytest.mark.asyncio
async def test_create_customer_new():
    """Test creating a new Stripe customer"""
    with patch('stripe.Customer.create') as mock_create:
        mock_create.return_value = MagicMock(id='cus_test123')

        customer_id = await create_customer(
            owner_id="patient_123",
            owner_type="PATIENT",
            email="test@example.com",
            name="Test Patient"
        )

        assert customer_id == 'cus_test123'
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_create_checkout_session():
    """Test creating Stripe checkout session"""
    with patch('stripe.checkout.Session.create') as mock_create:
        mock_create.return_value = MagicMock(
            id='cs_test123',
            url='https://checkout.stripe.com/test'
        )

        result = await create_checkout_session(
            customer_id='cus_test123',
            price_id='price_starter',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )

        assert result.session_id == 'cs_test123'
        assert result.checkout_url == 'https://checkout.stripe.com/test'

@pytest.mark.asyncio
async def test_cancel_subscription_immediate():
    """Test immediate subscription cancellation"""
    with patch('stripe.Subscription.list') as mock_list, \
         patch('stripe.Subscription.cancel') as mock_cancel:

        mock_list.return_value = MagicMock(
            data=[MagicMock(id='sub_test123')]
        )
        mock_cancel.return_value = MagicMock(
            id='sub_test123',
            status='canceled',
            canceled_at=1234567890,
            cancel_at_period_end=False
        )

        result = await cancel_subscription('cus_test123', cancel_immediately=True)

        assert result['subscription_id'] == 'sub_test123'
        assert result['status'] == 'canceled'
        mock_cancel.assert_called_once_with('sub_test123')

@pytest.mark.asyncio
async def test_refund_transaction_full(db_session):
    """Test full transaction refund"""
    # Create test transaction
    transaction = BillingTransaction(
        owner_id=uuid.uuid4(),
        owner_type="PATIENT",
        stripe_payment_intent_id="pi_test123",
        amount_cents=5000,
        currency="usd",
        status="SUCCEEDED"
    )
    db_session.add(transaction)
    await db_session.commit()

    with patch('stripe.Refund.create') as mock_refund:
        mock_refund.return_value = MagicMock(id='re_test123', amount=5000)

        result = await refund_transaction(
            db=db_session,
            transaction_id=transaction.id,
            amount_cents=None,  # Full refund
            reason="Customer request",
            refunded_by=uuid.uuid4()
        )

        assert result['refund_id'] == 're_test123'
        assert result['amount_refunded'] == 5000

        await db_session.refresh(transaction)
        assert transaction.status == "REFUNDED"

@pytest.mark.asyncio
async def test_grant_free_subscription(db_session):
    """Test granting free subscription"""
    patient_id = uuid.uuid4()
    admin_id = uuid.uuid4()

    override = await grant_free_subscription(
        db=db_session,
        owner_id=patient_id,
        owner_type="PATIENT",
        reason="Promotional offer",
        granted_by=admin_id,
        duration_months=12
    )

    assert override.owner_id == patient_id
    assert override.override_type == "FREE"
    assert override.granted_by == admin_id
    assert override.expires_at is not None
```

**`tests/api/test_patient_billing_api.py`:**
```python
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_create_patient_checkout_unauthorized(client: AsyncClient, test_patient):
    """Test checkout creation without authorization"""
    response = await client.post(
        f"/api/v1/patients/{test_patient.id}/billing/checkout",
        json={"price_id": "price_starter"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_patient_checkout_success(
    client: AsyncClient,
    test_patient,
    auth_headers_patient
):
    """Test successful checkout creation"""
    with patch('src.services.billing.create_checkout_session') as mock_checkout:
        mock_checkout.return_value = CheckoutSessionResponse(
            session_id='cs_test123',
            checkout_url='https://checkout.stripe.com/test'
        )

        response = await client.post(
            f"/api/v1/patients/{test_patient.id}/billing/checkout",
            json={"price_id": "price_starter"},
            headers=auth_headers_patient
        )

        assert response.status_code == 200
        data = response.json()
        assert data['session_id'] == 'cs_test123'
        assert 'checkout_url' in data

@pytest.mark.asyncio
async def test_get_patient_subscription(
    client: AsyncClient,
    test_patient,
    auth_headers_patient
):
    """Test getting patient subscription status"""
    response = await client.get(
        f"/api/v1/patients/{test_patient.id}/billing/subscription",
        headers=auth_headers_patient
    )

    assert response.status_code == 200
    data = response.json()
    assert 'status' in data

@pytest.mark.asyncio
async def test_cancel_patient_subscription_forbidden(
    client: AsyncClient,
    test_patient,
    auth_headers_different_user
):
    """Test cancellation by unauthorized user"""
    response = await client.post(
        f"/api/v1/patients/{test_patient.id}/billing/cancel",
        json={"cancel_immediately": False},
        headers=auth_headers_different_user
    )

    assert response.status_code == 403
```

**`tests/api/test_admin_billing_api.py`:**
```python
@pytest.mark.asyncio
async def test_list_subscriptions_admin_only(
    client: AsyncClient,
    auth_headers_non_admin
):
    """Test subscription list requires admin"""
    response = await client.get(
        "/api/v1/admin/billing/subscriptions",
        headers=auth_headers_non_admin
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_list_subscriptions_with_filters(
    client: AsyncClient,
    auth_headers_admin
):
    """Test subscription list with filters"""
    response = await client.get(
        "/api/v1/admin/billing/subscriptions",
        params={"status": "ACTIVE", "owner_type": "PATIENT"},
        headers=auth_headers_admin
    )

    assert response.status_code == 200
    data = response.json()
    assert 'subscriptions' in data
    assert 'total' in data

@pytest.mark.asyncio
async def test_refund_transaction_success(
    client: AsyncClient,
    test_transaction,
    auth_headers_admin
):
    """Test successful refund"""
    with patch('src.services.billing.refund_transaction') as mock_refund:
        mock_refund.return_value = {
            'refund_id': 're_test123',
            'amount_refunded': 5000
        }

        response = await client.post(
            f"/api/v1/admin/billing/transactions/{test_transaction.id}/refund",
            json={
                "transaction_id": str(test_transaction.id),
                "reason": "Customer request"
            },
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['refund_id'] == 're_test123'
```

**`tests/api/test_proxy_billing_api.py` (NEW):**
```python
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_proxy_list_managed_subscriptions(
    client: AsyncClient,
    test_proxy,
    test_managed_patient,
    auth_headers_proxy
):
    """Test proxy listing all managed patient subscriptions"""
    response = await client.get(
        "/api/v1/proxy/managed-patients/billing",
        headers=auth_headers_proxy
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(sub['patient_id'] == str(test_managed_patient.id) for sub in data)

@pytest.mark.asyncio
async def test_proxy_create_checkout_for_patient(
    client: AsyncClient,
    test_proxy,
    test_managed_patient,
    auth_headers_proxy
):
    """Test proxy creating checkout for managed patient"""
    with patch('src.services.billing.create_checkout_session') as mock_checkout:
        mock_checkout.return_value = CheckoutSessionResponse(
            session_id='cs_test123',
            checkout_url='https://checkout.stripe.com/test'
        )

        response = await client.post(
            f"/api/v1/proxy/managed-patients/{test_managed_patient.id}/billing/checkout",
            json={"price_id": "price_starter"},
            headers=auth_headers_proxy
        )

        assert response.status_code == 200
        data = response.json()
        assert data['session_id'] == 'cs_test123'

@pytest.mark.asyncio
async def test_proxy_cannot_manage_unassigned_patient(
    client: AsyncClient,
    test_proxy,
    test_other_patient,
    auth_headers_proxy
):
    """Test proxy cannot manage patient they're not assigned to"""
    response = await client.post(
        f"/api/v1/proxy/managed-patients/{test_other_patient.id}/billing/checkout",
        json={"price_id": "price_starter"},
        headers=auth_headers_proxy
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_assign_billing_manager(
    client: AsyncClient,
    test_patient,
    test_proxy_user,
    auth_headers_patient
):
    """Test assigning billing manager to patient"""
    response = await client.put(
        f"/api/v1/patients/{test_patient.id}/billing/manager",
        json={"proxy_user_id": str(test_proxy_user.id)},
        headers=auth_headers_patient
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True

@pytest.mark.asyncio
async def test_remove_billing_manager(
    client: AsyncClient,
    test_patient_with_manager,
    auth_headers_patient
):
    """Test removing billing manager from patient"""
    response = await client.delete(
        f"/api/v1/patients/{test_patient_with_manager.id}/billing/manager",
        headers=auth_headers_patient
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True

@pytest.mark.asyncio
async def test_admin_list_billing_managers(
    client: AsyncClient,
    auth_headers_admin
):
    """Test admin listing all billing manager relationships"""
    response = await client.get(
        "/api/v1/admin/billing/managers",
        headers=auth_headers_admin
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_billing_email_routed_to_proxy(
    db_session,
    test_patient_with_manager,
    test_proxy_user
):
    """Test billing emails sent to proxy when billing manager assigned"""
    from src.services.billing_access import get_billing_email_recipient

    email, name = await get_billing_email_recipient(db_session, test_patient_with_manager)

    assert email == test_proxy_user.email
    assert name == f"{test_proxy_user.first_name} {test_proxy_user.last_name}"
```

#### 2. Integration Tests: Webhook Handlers

**`tests/integration/test_webhooks.py`:**
```python
import pytest
from httpx import AsyncClient
import stripe
import hmac
import hashlib
import time

def generate_webhook_signature(payload: str, secret: str) -> str:
    """Generate Stripe webhook signature"""
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"

@pytest.mark.asyncio
async def test_webhook_payment_succeeded(client: AsyncClient, db_session, test_patient):
    """Test payment success webhook"""
    payload = {
        "id": "evt_test123",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_test123",
                "customer": test_patient.stripe_customer_id,
                "amount_paid": 7900,
                "currency": "usd",
                "payment_intent": "pi_test123",
                "hosted_invoice_url": "https://invoice.stripe.com/test",
                "number": "INV-001"
            }
        }
    }

    signature = generate_webhook_signature(
        json.dumps(payload),
        settings.STRIPE_WEBHOOK_SECRET
    )

    response = await client.post(
        "/api/v1/webhooks/stripe",
        json=payload,
        headers={"Stripe-Signature": signature}
    )

    assert response.status_code == 200

    # Verify transaction created
    transaction = await db_session.execute(
        select(BillingTransaction).where(
            BillingTransaction.stripe_invoice_id == "in_test123"
        )
    )
    transaction = transaction.scalar_one()
    assert transaction.amount_cents == 7900
    assert transaction.status == "SUCCEEDED"

@pytest.mark.asyncio
async def test_webhook_invalid_signature(client: AsyncClient):
    """Test webhook with invalid signature"""
    response = await client.post(
        "/api/v1/webhooks/stripe",
        json={"type": "test"},
        headers={"Stripe-Signature": "invalid"}
    )

    assert response.status_code == 400
```

#### 3. E2E Tests: Frontend

**`tests/e2e/patient-billing.spec.ts`:**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Patient Billing Flow', () => {
  test('patient can view billing page', async ({ page }) => {
    // Login as patient
    await page.goto('/login');
    await page.fill('[name=email]', 'patient@test.com');
    await page.fill('[name=password]', 'password123');
    await page.click('button[type=submit]');

    // Navigate to billing
    await page.goto('/patient/billing');
    await expect(page.locator('h1')).toContainText('My Billing');
  });

  test('patient can start checkout', async ({ page, context }) => {
    await page.goto('/patient/billing');

    // Click on Professional plan
    await page.click('text=Professional');
    await page.click('text=Get Started');

    // Wait for redirect to Stripe (will be blocked by CORS in test)
    // Check that checkout API was called
    await page.waitForURL(/checkout\.stripe\.com/);
  });

  test('patient can view transaction history', async ({ page }) => {
    // Assume patient has existing transactions
    await page.goto('/patient/billing');

    // Should see transaction history
    await expect(page.locator('text=Payment History')).toBeVisible();

    // Check table populated
    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(3, { timeout: 5000 });
  });

  test('patient can cancel subscription', async ({ page }) => {
    await page.goto('/patient/billing');

    // Click cancel button
    await page.click('text=Cancel Subscription');

    // Dialog should appear
    await expect(page.locator('[role=dialog]')).toBeVisible();

    // Click cancel at period end
    await page.click('text=Cancel at Period End');

    // Success message
    await expect(page.locator('text=Subscription cancelled')).toBeVisible();
  });
});
```

**`tests/e2e/proxy-billing.spec.ts` (NEW):**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Proxy Billing Management', () => {
  test('proxy can view managed patients billing dashboard', async ({ page }) => {
    // Login as proxy
    await page.goto('/login');
    await page.fill('[name=email]', 'proxy@test.com');
    await page.fill('[name=password]', 'password123');
    await page.click('button[type=submit]');

    // Navigate to proxy billing dashboard
    await page.goto('/proxy/managed-patients-billing');
    await expect(page.locator('h1')).toContainText('Managed Patients Billing');

    // Should see list of managed patients
    const patientCards = page.locator('[data-testid="patient-subscription-card"]');
    await expect(patientCards).toHaveCount(2, { timeout: 5000 });
  });

  test('proxy can create checkout for managed patient', async ({ page }) => {
    await page.goto('/proxy/managed-patients-billing');

    // Click on patient card
    await page.locator('[data-testid="patient-subscription-card"]').first().click();

    // Should see patient billing details
    await expect(page.locator('text=Patient: John Doe')).toBeVisible();

    // Click subscribe button
    await page.click('text=Subscribe to Professional');

    // Should redirect to Stripe
    await page.waitForURL(/checkout\.stripe\.com/);
  });

  test('proxy can view managed patient transaction history', async ({ page }) => {
    await page.goto('/proxy/managed-patients-billing');

    // Navigate to specific patient
    await page.click('[data-testid="view-patient-billing"]');

    // View transaction history
    await expect(page.locator('text=Payment History')).toBeVisible();
    const rows = page.locator('table tbody tr');
    await expect(rows).toHaveCount(1, { timeout: 5000 });
  });

  test('proxy cannot access unmanaged patient billing', async ({ page }) => {
    // Try to directly access unmanaged patient billing
    await page.goto('/proxy/managed-patients/unmanaged-patient-id/billing');

    // Should see 403 error or redirect
    await expect(page.locator('text=Access Denied')).toBeVisible();
  });

  test('patient can assign billing manager', async ({ page }) => {
    // Login as patient
    await page.goto('/login');
    await page.fill('[name=email]', 'patient@test.com');
    await page.fill('[name=password]', 'password123');
    await page.click('button[type=submit]');

    // Navigate to billing
    await page.goto('/patient/billing');

    // Click assign billing manager
    await page.click('text=Assign Billing Manager');

    // Select proxy from dropdown
    await page.click('[role=combobox]');
    await page.click('text=Jane Smith (Proxy)');

    // Submit
    await page.click('button:has-text("Assign Manager")');

    // Success message
    await expect(page.locator('text=Billing manager assigned')).toBeVisible();

    // Should see manager card
    await expect(page.locator('text=Managed by: Jane Smith')).toBeVisible();
  });

  test('patient can remove billing manager', async ({ page }) => {
    await page.goto('/patient/billing');

    // Should see billing manager card
    await expect(page.locator('text=Managed by:')).toBeVisible();

    // Click remove
    await page.click('text=Remove Billing Manager');

    // Confirm
    await page.click('button:has-text("Remove Manager")');

    // Success message
    await expect(page.locator('text=Billing manager removed')).toBeVisible();
  });
});
```

**`tests/e2e/admin-billing.spec.ts`:**
```typescript
test.describe('Admin Billing Dashboard', () => {
  test('admin can view all subscriptions', async ({ page }) => {
    await page.goto('/admin/billing-management');

    // Should see analytics cards
    await expect(page.locator('text=Total MRR')).toBeVisible();
    await expect(page.locator('text=Active Subscriptions')).toBeVisible();

    // Should see subscriptions table
    const table = page.locator('table');
    await expect(table).toBeVisible();
  });

  test('admin can filter subscriptions', async ({ page }) => {
    await page.goto('/admin/billing-management');

    // Apply status filter
    await page.click('[role=combobox]');
    await page.click('text=Active');

    // Table should update
    await page.waitForTimeout(1000);
    const rows = page.locator('table tbody tr');
    await expect(rows.first()).toBeVisible();
  });

  test('admin can grant free subscription', async ({ page }) => {
    await page.goto('/admin/billing-management');

    // Click actions menu
    await page.locator('button[aria-label="Actions"]').first().click();

    // Click grant free
    await page.click('text=Grant Free Subscription');

    // Fill form
    await page.fill('[name=duration]', '12');
    await page.fill('[name=reason]', 'Promotional offer');

    // Submit
    await page.click('text=Grant Free Subscription');

    // Success message
    await expect(page.locator('text=granted successfully')).toBeVisible();
  });

  test('admin can issue refund', async ({ page }) => {
    await page.goto('/admin/billing-management');

    // Go to transactions tab
    await page.click('text=Transactions');

    // Click refund button
    await page.locator('button:has-text("Refund")').first().click();

    // Fill reason
    await page.fill('[name=reason]', 'Customer request');

    // Submit
    await page.click('button:has-text("Issue Refund")');

    // Success message
    await expect(page.locator('text=Refund processed')).toBeVisible();
  });

  test('admin can view billing managers tab', async ({ page }) => {
    await page.goto('/admin/billing-management');

    // Go to billing managers tab
    await page.click('text=Billing Managers');

    // Should see billing manager relationships table
    await expect(page.locator('text=Patient')).toBeVisible();
    await expect(page.locator('text=Billing Manager')).toBeVisible();

    // Should show relationships
    const rows = page.locator('table tbody tr');
    await expect(rows.first()).toBeVisible();
  });

  test('admin can remove billing manager', async ({ page }) => {
    await page.goto('/admin/billing-management');

    // Go to billing managers tab
    await page.click('text=Billing Managers');

    // Click remove button
    await page.locator('button:has-text("Remove")').first().click();

    // Confirm
    await page.click('button:has-text("Remove Billing Manager")');

    // Success message
    await expect(page.locator('text=removed successfully')).toBeVisible();
  });

  test('admin can see billing manager in subscriptions list', async ({ page }) => {
    await page.goto('/admin/billing-management');

    // Should see Billing Manager column
    await expect(page.locator('th:has-text("Billing Manager")')).toBeVisible();

    // Should show manager names for managed subscriptions
    const managerCell = page.locator('td:has-text("Managed")').first();
    await expect(managerCell).toBeVisible();
  });
});
```

#### 4. Load/Performance Tests

**`tests/load/test_billing_load.py`:**
```python
from locust import HttpUser, task, between

class BillingUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before tests"""
        self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })

    @task(3)
    def view_subscription(self):
        """View subscription status"""
        self.client.get("/api/v1/patients/test-patient-id/billing/subscription")

    @task(2)
    def view_transactions(self):
        """View transaction history"""
        self.client.get("/api/v1/patients/test-patient-id/billing/transactions")

    @task(1)
    def create_checkout(self):
        """Create checkout session"""
        self.client.post(
            "/api/v1/patients/test-patient-id/billing/checkout",
            json={"price_id": "price_starter"}
        )

# Run: locust -f tests/load/test_billing_load.py --host=http://localhost:8000
```

#### 5. Documentation

**`docs/billing-system.md`:**
```markdown
# Billing System Documentation

## Overview
Complete Stripe-integrated billing system supporting both organization and patient-level subscriptions.

## Architecture
[Diagrams and architecture overview from Epic 22 index.md]

## API Endpoints

### Patient Billing
- `POST /api/v1/patients/{id}/billing/checkout` - Create checkout session
- `GET /api/v1/patients/{id}/billing/subscription` - Get subscription status
- `POST /api/v1/patients/{id}/billing/portal` - Access billing portal
- `GET /api/v1/patients/{id}/billing/transactions` - List transactions
- `POST /api/v1/patients/{id}/billing/cancel` - Cancel subscription
- `PUT /api/v1/patients/{id}/billing/manager` - Assign billing manager
- `DELETE /api/v1/patients/{id}/billing/manager` - Remove billing manager

### Proxy Billing
- `GET /api/v1/proxy/managed-patients/billing` - List all managed patient subscriptions
- `GET /api/v1/proxy/managed-patients/{id}/billing/subscription` - Get patient subscription
- `POST /api/v1/proxy/managed-patients/{id}/billing/checkout` - Create checkout for patient
- `POST /api/v1/proxy/managed-patients/{id}/billing/cancel` - Cancel patient subscription
- `GET /api/v1/proxy/managed-patients/{id}/billing/transactions` - View patient transactions

### Admin Billing
- `GET /api/v1/admin/billing/subscriptions` - List all subscriptions
- `POST /api/v1/admin/billing/transactions/{id}/refund` - Refund transaction
- `POST /api/v1/admin/billing/grant-free` - Grant free subscription
- `GET /api/v1/admin/billing/analytics` - Get billing analytics
- `GET /api/v1/admin/billing/managers` - List all billing manager relationships
- `PUT /api/v1/admin/patients/{id}/billing/manager` - Admin assign billing manager
- `DELETE /api/v1/admin/patients/{id}/billing/manager` - Admin remove billing manager

## Webhooks
[List of all webhook events and handlers]

## Email Notifications
[List of all email templates and triggers]

## Configuration
[Environment variables and setup instructions]

## Testing
[Test coverage and how to run tests]

## Monitoring
[Metrics, alerts, and dashboards]

## Troubleshooting
[Common issues and solutions]

## Security
[Security considerations and compliance]
```

**API Documentation Updates:**
Add OpenAPI/Swagger documentation for all new endpoints using FastAPI's automatic documentation.

#### 6. Test Coverage Configuration

**`.coveragerc`:**
```ini
[run]
source = src
omit =
    */tests/*
    */migrations/*
    */__pycache__/*

[report]
precision = 2
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

**`pytest.ini`:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
```

## Acceptance Criteria
### Test Coverage
- [ ] >90% test coverage for all billing code.
- [ ] Unit tests for all service functions.
- [ ] Integration tests for all API endpoints.
- [ ] Webhook integration tests with signature verification.
- [ ] Load tests show system handles 100 concurrent users.
- [ ] All tests pass in CI pipeline.

### Patient Billing Tests
- [ ] E2E tests for patient billing flow.
- [ ] E2E tests for patient subscription management.
- [ ] E2E tests for billing manager assignment.

### Proxy Billing Tests
- [ ] API tests for proxy billing endpoints.
- [ ] E2E tests for proxy managed patients dashboard.
- [ ] E2E tests for proxy checkout creation.
- [ ] Tests for proxy access control (cannot manage unassigned patients).
- [ ] Tests for billing email routing to proxy.

### Admin Billing Tests
- [ ] E2E tests for admin billing dashboard.
- [ ] E2E tests for billing manager management.
- [ ] Tests for admin billing manager assignment/removal.
- [ ] Tests for billing manager display in subscriptions list.

### Documentation
- [ ] API documentation updated in Swagger/OpenAPI.
- [ ] User documentation created (patient, proxy, admin).
- [ ] Developer documentation created.
- [ ] Proxy billing guide created.
- [ ] All edge cases covered in tests.

## Verification Plan
**Test Execution:**
```bash
# Backend unit tests
pytest tests/ -v --cov=src --cov-report=html

# Backend integration tests
pytest tests/integration/ -v

# Frontend unit tests
pnpm test --run --coverage

# E2E tests
pnpm exec playwright test

# Load tests
locust -f tests/load/test_billing_load.py --headless -u 100 -r 10 -t 5m
```

**Coverage Report:**
```bash
# Generate coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Check coverage threshold
pytest --cov=src --cov-fail-under=90
```

**Documentation Review:**
1. Review API documentation in Swagger UI
2. Verify all endpoints documented
3. Test example requests/responses
4. Review user-facing docs for completeness
5. Validate code comments and docstrings

## Test Scenarios to Cover

### Happy Paths - Patient Billing
- [ ] Patient signs up for subscription
- [ ] Patient views billing history
- [ ] Patient cancels subscription
- [ ] Patient assigns billing manager
- [ ] Patient removes billing manager

### Happy Paths - Proxy Billing
- [ ] Proxy views managed patients billing dashboard
- [ ] Proxy creates checkout for managed patient
- [ ] Proxy cancels subscription for managed patient
- [ ] Proxy views transaction history for managed patient
- [ ] Billing emails sent to proxy instead of patient

### Happy Paths - Admin Billing
- [ ] Admin grants free subscription
- [ ] Admin issues refund
- [ ] Admin views all billing manager relationships
- [ ] Admin assigns billing manager (bypasses proxy check)
- [ ] Admin removes billing manager

### Error Cases - General
- [ ] Checkout with invalid price ID
- [ ] Access billing without authentication
- [ ] Cancel non-existent subscription
- [ ] Refund already-refunded transaction
- [ ] Webhook with invalid signature
- [ ] Payment failure handling

### Error Cases - Proxy Billing
- [ ] Proxy attempts to manage unassigned patient
- [ ] Proxy without active proxy relationship attempts billing action
- [ ] Non-proxy user attempts proxy billing endpoints
- [ ] Assign billing manager to non-existent proxy

### Edge Cases - General
- [ ] Concurrent checkout sessions
- [ ] Subscription change during billing period
- [ ] Partial refunds
- [ ] Expired free subscription
- [ ] Customer with no payment method
- [ ] Duplicate webhook events

### Edge Cases - Proxy Billing
- [ ] Proxy relationship revoked while billing manager assigned
- [ ] Multiple proxies assigned as billing managers (should not happen)
- [ ] Patient removes billing manager during active proxy session
- [ ] Billing manager assignment while checkout in progress

### Security Tests
- [ ] Unauthorized access attempts to proxy billing endpoints
- [ ] SQL injection attempts in billing manager assignment
- [ ] XSS in billing forms
- [ ] CSRF protection on billing actions
- [ ] Rate limiting enforcement on billing operations
- [ ] Audit logging for all proxy billing actions

## Documentation Checklist
### API Documentation
- [ ] API endpoint documentation (OpenAPI)
- [ ] Patient billing API endpoints
- [ ] Proxy billing API endpoints
- [ ] Admin billing API endpoints
- [ ] Billing manager API endpoints

### User Documentation
- [ ] User guide for patients (billing signup, management)
- [ ] User guide for proxies (managing patient billing)
- [ ] User guide for billing manager assignment
- [ ] Admin guide for billing management
- [ ] Admin guide for billing manager oversight

### Technical Documentation
- [ ] Developer setup instructions
- [ ] Webhook configuration guide
- [ ] Database schema documentation (billing_manager_id fields)
- [ ] Email routing logic documentation
- [ ] Access control flow documentation

### Operational Documentation
- [ ] Troubleshooting guide
- [ ] Security best practices
- [ ] Compliance documentation (PCI-DSS)
- [ ] Audit logging guide
- [ ] Monitoring and metrics guide

## Rollback Plan
If test failures block deployment:
1. Identify failing tests
2. Determine if bugs or test issues
3. Fix critical bugs immediately
4. Skip non-critical tests temporarily
5. Create tickets for test fixes
6. Deploy with known limitations documented
