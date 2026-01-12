# Proxy Billing Management - Implementation Addendum

## Overview
This document outlines the proxy-specific additions to Epic 22 stories to enable proxies to manage billing on behalf of patients.

## Key Requirements
1. **Subscription Ownership**: Subscriptions remain 1-1 with patients (patient_id, not proxy_id)
2. **Billing Manager**: Formal `billing_manager_id` field on Patient model
3. **Multi-Patient Management**: Proxy can manage multiple patient subscriptions
4. **Email Routing**: Billing emails sent to proxy when they are billing manager
5. **Access Control**: Proxy must have active proxy relationship to manage billing

---

## Story 22.1: Patient Billing API - Proxy Additions

### 1. Patient Model Updates (`backend/src/models/profiles.py`)

```python
class Patient(Base):
    # ... existing fields ...

    # NEW: Billing Manager fields
    billing_manager_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        comment="Proxy user who manages billing for this patient"
    )
    billing_manager_assigned_at: Mapped[datetime | None]
    billing_manager_assigned_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    # Relationships
    billing_manager: Mapped["User"] = relationship(
        "User",
        foreign_keys=[billing_manager_id],
        back_populates="managed_patient_billing"
    )
```

### 2. Billing Transaction Model Updates

```python
class BillingTransaction(Base):
    # ... existing fields ...

    # NEW: Track if proxy initiated transaction
    managed_by_proxy_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        comment="Proxy user who initiated this transaction"
    )
```

### 3. Access Control Helper (`backend/src/services/billing_access.py` - NEW)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.profiles import Patient
from ..models.proxies import PatientProxy
from uuid import UUID

async def can_manage_billing(
    db: AsyncSession,
    user_id: UUID,
    patient_id: UUID
) -> tuple[bool, str]:
    """
    Check if user can manage billing for patient.

    Returns: (can_manage: bool, reason: str)

    Access granted if:
    1. User is the patient themselves
    2. User is designated billing manager (billing_manager_id)
    3. User is active proxy with billing access AND is billing manager
    """
    # Get patient
    patient = await db.get(Patient, patient_id)
    if not patient:
        return False, "Patient not found"

    # Check if user is the patient
    if patient.user_id == user_id:
        return True, "Patient managing own billing"

    # Check if user is billing manager
    if patient.billing_manager_id == user_id:
        # Verify proxy relationship still active
        proxy_rel = await db.execute(
            select(PatientProxy).where(
                PatientProxy.patient_id == patient_id,
                PatientProxy.proxy_user_id == user_id,
                PatientProxy.status == "ACTIVE"
            )
        )
        if proxy_rel.scalar_one_or_none():
            return True, "Proxy is billing manager"
        else:
            return False, "Proxy relationship no longer active"

    return False, "User not authorized to manage billing"

async def get_billing_email_recipient(
    db: AsyncSession,
    patient: Patient
) -> tuple[str, str]:
    """
    Get email and name for billing notifications.

    Returns: (email: str, name: str)

    If billing_manager_id is set, returns proxy's email.
    Otherwise returns patient's email.
    """
    if patient.billing_manager_id:
        # Send to billing manager (proxy)
        from ..models.users import User
        manager = await db.get(User, patient.billing_manager_id)
        if manager:
            return manager.email, f"{manager.first_name} {manager.last_name}"

    # Send to patient
    return patient.email, f"{patient.first_name} {patient.last_name}"
```

### 4. New Schemas (`backend/src/schemas/billing.py` - ADD)

```python
class AssignBillingManagerRequest(BaseModel):
    proxy_user_id: UUID

class AssignBillingManagerResponse(BaseModel):
    success: bool
    message: str
    billing_manager_id: UUID
    assigned_at: datetime

class ManagedPatientSubscription(BaseModel):
    patient_id: UUID
    patient_name: str
    subscription_status: str
    plan_id: str | None
    current_period_end: datetime | None
    mrr_cents: int
```

### 5. New API Endpoints

#### A. Patient Billing Manager Assignment (`backend/src/api/patients_billing.py`)

```python
@router.put("/{patient_id}/billing/manager", response_model=AssignBillingManagerResponse)
async def assign_billing_manager(
    patient_id: str,
    request: AssignBillingManagerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign proxy as billing manager for patient"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    # Verify requester is patient or admin
    if current_user.id != patient.user_id and not current_user.is_admin:
        raise HTTPException(403, "Not authorized")

    # Verify proxy relationship exists and is active
    proxy_rel = await db.execute(
        select(PatientProxy).where(
            PatientProxy.patient_id == patient_id,
            PatientProxy.proxy_user_id == request.proxy_user_id,
            PatientProxy.status == "ACTIVE"
        )
    )
    if not proxy_rel.scalar_one_or_none():
        raise HTTPException(400, "No active proxy relationship")

    # Assign billing manager
    patient.billing_manager_id = request.proxy_user_id
    patient.billing_manager_assigned_at = datetime.utcnow()
    patient.billing_manager_assigned_by = current_user.id

    await db.commit()

    return AssignBillingManagerResponse(
        success=True,
        message="Billing manager assigned successfully",
        billing_manager_id=request.proxy_user_id,
        assigned_at=patient.billing_manager_assigned_at
    )

@router.delete("/{patient_id}/billing/manager")
async def remove_billing_manager(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove billing manager from patient"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    # Verify requester is patient, billing manager, or admin
    if (current_user.id != patient.user_id and
        current_user.id != patient.billing_manager_id and
        not current_user.is_admin):
        raise HTTPException(403, "Not authorized")

    patient.billing_manager_id = None
    patient.billing_manager_assigned_at = None
    patient.billing_manager_assigned_by = None

    await db.commit()

    return {"success": True, "message": "Billing manager removed"}
```

#### B. Proxy Billing Management (`backend/src/api/proxy_billing.py` - NEW)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.profiles import Patient
from ..services.billing_access import can_manage_billing, get_billing_email_recipient
from ..services import billing as billing_service
from ..auth import get_current_user, User

router = APIRouter()

@router.get("/managed-patients/billing", response_model=list[ManagedPatientSubscription])
async def list_managed_patient_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all patient subscriptions managed by this proxy"""
    # Find all patients where current user is billing manager
    query = select(Patient).where(
        Patient.billing_manager_id == current_user.id
    )
    result = await db.execute(query)
    patients = result.scalars().all()

    subscriptions = []
    for patient in patients:
        # Get subscription status from Stripe if customer exists
        if patient.stripe_customer_id:
            status = await billing_service.get_subscription_status(patient.stripe_customer_id)
        else:
            status = {"status": "NONE", "plan_id": None, "current_period_end": None}

        subscriptions.append(ManagedPatientSubscription(
            patient_id=patient.id,
            patient_name=f"{patient.first_name} {patient.last_name}",
            subscription_status=status["status"],
            plan_id=status.get("plan_id"),
            current_period_end=status.get("current_period_end"),
            mrr_cents=0  # Calculate from plan
        ))

    return subscriptions

@router.post("/managed-patients/{patient_id}/billing/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_for_patient(
    patient_id: str,
    request: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create checkout session for patient (as billing manager)"""
    # Verify access
    can_manage, reason = await can_manage_billing(db, current_user.id, patient_id)
    if not can_manage:
        raise HTTPException(403, reason)

    patient = await db.get(Patient, patient_id)

    # Get or create Stripe customer
    customer_id = await billing_service.get_or_create_patient_customer(patient_id, db)

    # Create checkout session
    session = await billing_service.create_checkout_session(
        customer_id=customer_id,
        price_id=request.price_id,
        success_url=f"{settings.FRONTEND_URL}/proxy/billing/success",
        cancel_url=f"{settings.FRONTEND_URL}/proxy/managed-patients/billing"
    )

    # Log that proxy initiated checkout
    await billing_audit.log_checkout_created(
        db=db,
        user_id=current_user.id,
        owner_id=patient_id,
        owner_type="PATIENT",
        price_id=request.price_id,
        session_id=session.session_id,
        metadata={"managed_by_proxy": True}
    )

    return session

@router.get("/managed-patients/{patient_id}/billing/transactions", response_model=TransactionListResponse)
async def get_patient_transactions(
    patient_id: str,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transaction history for managed patient"""
    # Verify access
    can_manage, reason = await can_manage_billing(db, current_user.id, patient_id)
    if not can_manage:
        raise HTTPException(403, reason)

    # Query transactions (reuse existing logic)
    # ... similar to patient transaction endpoint ...
    pass

@router.post("/managed-patients/{patient_id}/billing/cancel", response_model=CancelSubscriptionResponse)
async def cancel_patient_subscription(
    patient_id: str,
    request: CancelSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel subscription for managed patient"""
    # Verify access
    can_manage, reason = await can_manage_billing(db, current_user.id, patient_id)
    if not can_manage:
        raise HTTPException(403, reason)

    patient = await db.get(Patient, patient_id)
    if not patient.stripe_customer_id:
        raise HTTPException(400, "No active subscription")

    result = await billing_service.cancel_subscription(
        customer_id=patient.stripe_customer_id,
        cancel_immediately=request.cancel_immediately
    )

    # Log proxy action
    await billing_audit.log_subscription_cancelled(
        db=db,
        user_id=current_user.id,
        owner_id=patient_id,
        owner_type="PATIENT",
        reason=request.reason,
        cancelled_immediately=request.cancel_immediately,
        metadata={"managed_by_proxy": True}
    )

    return CancelSubscriptionResponse(
        success=True,
        cancelled_at=datetime.fromtimestamp(result["cancelled_at"]) if result["cancelled_at"] else None,
        cancels_at_period_end=result["cancels_at_period_end"],
        message="Subscription cancelled successfully"
    )
```

### 6. Update Patient Billing Endpoints Access Control

```python
# In patients_billing.py - update access control checks

@router.post("/{patient_id}/billing/checkout", response_model=CheckoutSessionResponse)
async def create_patient_checkout(
    patient_id: str,
    request: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create checkout session for patient subscription"""
    # NEW: Use billing access helper
    can_manage, reason = await can_manage_billing(db, current_user.id, patient_id)
    if not can_manage:
        raise HTTPException(403, reason)

    # ... rest of implementation ...
```

### 7. Router Registration (`backend/src/main.py`)

```python
from .api import proxy_billing

app.include_router(
    proxy_billing.router,
    prefix=f"{settings.API_V1_STR}/proxy",
    tags=["proxy-billing"]
)
```

---

## Story 22.2: Email & Receipts - Proxy Additions

### Email Service Updates (`backend/src/services/email.py`)

Update all billing email functions to route to billing manager:

```python
async def send_payment_success_email(
    db: AsyncSession,  # ADD db parameter
    patient: Patient,  # Pass full patient object
    amount_cents: int,
    receipt_number: str,
    payment_date: datetime,
    payment_method: str,
    plan_name: str,
    billing_period: str,
    receipt_url: str,
    pdf_attachment: bytes
):
    """Send payment success confirmation with receipt"""
    # NEW: Get email recipient (patient or billing manager)
    recipient_email, recipient_name = await get_billing_email_recipient(db, patient)

    template = env.get_template("emails/billing/payment-success.html")

    html_content = template.render(
        patient_name=recipient_name,  # Changed from patient name to recipient
        patient_email=recipient_email,
        actual_patient_name=f"{patient.first_name} {patient.last_name}",  # NEW: for email body
        is_proxy_managed=patient.billing_manager_id is not None,  # NEW: flag
        amount_dollars=f"{amount_cents / 100:.2f}",
        # ... rest of parameters ...
    )

    await send_email(
        to_email=recipient_email,  # Send to proxy if assigned
        subject=f"Payment Successful - Receipt {receipt_number}",
        html_content=html_content,
        attachments=[{
            "filename": f"receipt-{receipt_number}.pdf",
            "content": pdf_attachment,
            "content_type": "application/pdf"
        }]
    )
```

### Email Template Updates

Update `payment-success.html`:

```html
<p>Hi {{ patient_name }},</p>

{% if is_proxy_managed %}
<p>This is a billing notification for <strong>{{ actual_patient_name }}</strong>'s subscription,
which you manage as their billing manager.</p>
{% endif %}

<p>Thank you for your payment. The subscription is now active.</p>
<!-- rest of template -->
```

Similar updates needed for:
- `payment-failed.html`
- `subscription-cancelled.html`
- `upcoming-renewal.html`

---

## Story 22.3: Patient Billing Frontend - Proxy Additions

### 1. New Proxy Hooks (`frontend/src/hooks/api/useProxyBilling.ts`)

```typescript
export function useManagedPatientSubscriptions() {
  return useQuery({
    queryKey: ['proxy-managed-subscriptions'],
    queryFn: async () => {
      const { data } = await apiClient.get('/proxy/managed-patients/billing');
      return data;
    },
  });
}

export function useProxyCheckout(patientId: string) {
  return useMutation({
    mutationFn: async (priceId: string) => {
      const { data } = await apiClient.post(
        `/proxy/managed-patients/${patientId}/billing/checkout`,
        { price_id: priceId }
      );
      window.location.href = data.checkout_url;
      return data;
    },
  });
}

export function useAssignBillingManager(patientId: string) {
  return useMutation({
    mutationFn: async (proxyUserId: string) => {
      const { data } = await apiClient.put(
        `/patients/${patientId}/billing/manager`,
        { proxy_user_id: proxyUserId }
      );
      return data;
    },
  });
}
```

### 2. Proxy Billing Dashboard (`frontend/src/routes/_auth/proxy/managed-patients-billing.tsx`)

```typescript
export const Route = createFileRoute('/_auth/proxy/managed-patients-billing')({
  component: ProxyManagedPatientsBilling,
});

function ProxyManagedPatientsBilling() {
  const { data: subscriptions, isLoading } = useManagedPatientSubscriptions();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Managed Patient Billing</h1>
      <p className="text-muted-foreground mb-6">
        You are managing billing for {subscriptions?.length || 0} patient(s)
      </p>

      <div className="grid gap-4">
        {subscriptions?.map((sub) => (
          <Card key={sub.patient_id}>
            <CardHeader>
              <CardTitle>{sub.patient_name}</CardTitle>
              <CardDescription>
                Status: <Badge>{sub.subscription_status}</Badge>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center">
                <div>
                  <p>Plan: {sub.plan_id || 'No active plan'}</p>
                  {sub.current_period_end && (
                    <p className="text-sm text-muted-foreground">
                      Next billing: {formatDate(new Date(sub.current_period_end * 1000))}
                    </p>
                  )}
                </div>
                <Button asChild>
                  <Link to={`/proxy/managed-patients/${sub.patient_id}/billing`}>
                    Manage
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

### 3. Billing Manager Assignment Component (`frontend/src/components/billing/BillingManagerAssignment.tsx`)

```typescript
interface Props {
  patientId: string;
  currentBillingManagerId?: string;
  availableProxies: Array<{ id: string; name: string; email: string }>;
}

export function BillingManagerAssignment({ patientId, currentBillingManagerId, availableProxies }: Props) {
  const assignMutation = useAssignBillingManager(patientId);
  const [selectedProxy, setSelectedProxy] = useState(currentBillingManagerId);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Billing Manager</CardTitle>
        <CardDescription>
          Designate a proxy to manage billing for this patient
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Select value={selectedProxy} onValueChange={setSelectedProxy}>
          <SelectTrigger>
            <SelectValue placeholder="Select a proxy..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Patient manages own billing</SelectItem>
            {availableProxies.map((proxy) => (
              <SelectItem key={proxy.id} value={proxy.id}>
                {proxy.name} ({proxy.email})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          className="mt-4"
          onClick={() => assignMutation.mutate(selectedProxy!)}
          disabled={!selectedProxy || selectedProxy === 'none'}
        >
          Assign Billing Manager
        </Button>
      </CardContent>
    </Card>
  );
}
```

---

## Story 22.4: Admin Billing API - Proxy Additions

### Admin Endpoints for Billing Manager Management

```python
@router.get("/billing/managers", response_model=list[BillingManagerRelationship])
async def list_billing_managers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """List all billing manager relationships"""
    query = select(Patient).where(
        Patient.billing_manager_id.is_not(None)
    )
    result = await db.execute(query)
    patients = result.scalars().all()

    relationships = []
    for patient in patients:
        manager = await db.get(User, patient.billing_manager_id)
        relationships.append(BillingManagerRelationship(
            patient_id=patient.id,
            patient_name=f"{patient.first_name} {patient.last_name}",
            billing_manager_id=patient.billing_manager_id,
            billing_manager_name=f"{manager.first_name} {manager.last_name}",
            assigned_at=patient.billing_manager_assigned_at,
            assigned_by=patient.billing_manager_assigned_by
        ))

    return relationships

@router.put("/patients/{patient_id}/billing/manager")
async def admin_assign_billing_manager(
    patient_id: str,
    request: AssignBillingManagerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Admin assigns billing manager (bypasses proxy relationship check)"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    patient.billing_manager_id = request.proxy_user_id
    patient.billing_manager_assigned_at = datetime.utcnow()
    patient.billing_manager_assigned_by = current_user.id

    await db.commit()

    return {"success": True, "message": "Billing manager assigned"}
```

---

## Story 22.5: Admin Billing Frontend - Proxy Additions

### Subscription List Updates

Add "Billing Manager" column to admin subscriptions table:

```typescript
<TableHead>Billing Manager</TableHead>

// In table body:
<TableCell>
  {subscription.billing_manager_name ? (
    <div>
      <div className="font-medium">{subscription.billing_manager_name}</div>
      <Badge variant="outline" className="text-xs">Proxy Managed</Badge>
    </div>
  ) : (
    <span className="text-muted-foreground text-sm">Self-managed</span>
  )}
</TableCell>
```

### Billing Manager Management Tab

Add new tab to admin billing dashboard showing all billing manager relationships with ability to assign/remove.

---

## Story 22.6: Logging & Monitoring - Proxy Additions

### Audit Events

```python
class AuditEventType:
    # ... existing events ...

    BILLING_MANAGER_ASSIGNED = "billing.manager.assigned"
    BILLING_MANAGER_REMOVED = "billing.manager.removed"
    BILLING_PROXY_CHECKOUT_CREATED = "billing.proxy.checkout.created"
    BILLING_PROXY_SUBSCRIPTION_CANCELLED = "billing.proxy.subscription.cancelled"
```

### Metrics

```python
# Track proxy billing activity
proxy_managed_subscriptions = Gauge(
    'billing_proxy_managed_subscriptions',
    'Number of subscriptions managed by proxies'
)

proxy_billing_actions = Counter(
    'billing_proxy_actions_total',
    'Total number of billing actions by proxies',
    ['action_type', 'proxy_id']
)
```

---

## Story 22.7: Testing - Proxy Additions

### Test Cases

```python
@pytest.mark.asyncio
async def test_proxy_create_checkout_for_patient(client, test_proxy, test_patient, auth_headers_proxy):
    """Test proxy creates checkout for managed patient"""
    # Assign proxy as billing manager
    test_patient.billing_manager_id = test_proxy.id

    response = await client.post(
        f"/api/v1/proxy/managed-patients/{test_patient.id}/billing/checkout",
        json={"price_id": "price_starter"},
        headers=auth_headers_proxy
    )

    assert response.status_code == 200
    assert "checkout_url" in response.json()

@pytest.mark.asyncio
async def test_proxy_cannot_manage_without_assignment(client, test_proxy, test_patient, auth_headers_proxy):
    """Test proxy cannot manage billing without being assigned"""
    # No billing_manager_id set

    response = await client.post(
        f"/api/v1/proxy/managed-patients/{test_patient.id}/billing/checkout",
        json={"price_id": "price_starter"},
        headers=auth_headers_proxy
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_billing_email_sent_to_proxy(db_session, test_patient, test_proxy):
    """Test billing emails sent to proxy when assigned as billing manager"""
    test_patient.billing_manager_id = test_proxy.id

    email, name = await get_billing_email_recipient(db_session, test_patient)

    assert email == test_proxy.email
    assert name == f"{test_proxy.first_name} {test_proxy.last_name}"
```

### E2E Tests

```typescript
test('proxy can manage multiple patient subscriptions', async ({ page }) => {
  // Login as proxy
  await page.goto('/login');
  // ... login ...

  // Navigate to managed patients billing
  await page.goto('/proxy/managed-patients-billing');

  // Should see list of patients
  await expect(page.locator('text=Managed Patient Billing')).toBeVisible();

  // Click manage for first patient
  await page.locator('button:has-text("Manage")').first().click();

  // Should be able to start checkout
  await page.click('text=Get Started');

  // Verify redirect to Stripe
  await page.waitForURL(/checkout\.stripe\.com/);
});
```

---

## Summary of Changes

### Database
- Add 3 fields to `patients` table (`billing_manager_id`, `billing_manager_assigned_at`, `billing_manager_assigned_by`)
- Add `managed_by_proxy_id` to `billing_transactions` table

### Backend
- New service: `billing_access.py` with access control helpers
- New API router: `proxy_billing.py` with 5 endpoints
- Update patient billing endpoints to use new access control
- Update email service to route to billing manager
- Update audit logging for proxy actions

### Frontend
- New hooks: `useProxyBilling.ts`
- New page: `proxy/managed-patients-billing.tsx`
- New component: `BillingManagerAssignment.tsx`
- Update patient billing page to show billing manager assignment
- Update admin billing to show billing manager relationships

### Total New Endpoints
- 2 patient billing manager endpoints
- 5 proxy billing endpoints
- 2 admin billing manager endpoints

### Email Templates
- Update 4 templates to support proxy recipient routing

### Tests
- 10+ new test cases for proxy billing
- 3+ new E2E test scenarios
