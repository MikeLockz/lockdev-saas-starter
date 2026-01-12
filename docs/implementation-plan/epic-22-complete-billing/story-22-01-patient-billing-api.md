# Story 22.1: Patient Billing API & Database
**User Story:** As a Patient or Proxy, I want to manage subscriptions through API endpoints, so that I can pay for services independently or on behalf of patients I manage.

## Status
- [ ] **Pending**

## Context
- **Epic:** Epic 22 - Complete Billing & Subscription Management
- **Dependencies:**
  - Epic 15 (Billing) - existing Stripe integration
  - Epic 14 (Proxies) - proxy relationship model
- **Existing Code:**
  - `backend/src/services/billing.py` - Stripe service (org-level)
  - `backend/src/models/profiles.py` - Patient model with `stripe_customer_id`
  - `backend/src/api/webhooks.py` - Webhook handler (supports patients)
  - `backend/src/models/proxies.py` - Proxy relationship model

## Proxy Billing Requirements
**Key Feature:** Proxies can manage billing for patients they have access to.

- Subscriptions are 1-1 with patients (linked to patient_id, not proxy_id)
- Patient model has `billing_manager_id` field (references user_id of proxy)
- Proxy can manage multiple patient subscriptions
- Proxy must have active proxy relationship with patient to manage billing
- Billing emails sent to proxy when proxy is billing manager

## Technical Specification
**Goal:** Implement patient-specific billing endpoints and track payment transactions.

### Changes Required

#### 1. Database Migration: `backend/migrations/versions/xxx_billing_transactions.py`
```sql
-- Add billing manager fields to patients table
ALTER TABLE patients ADD COLUMN billing_manager_id UUID REFERENCES users(id);
ALTER TABLE patients ADD COLUMN billing_manager_assigned_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE patients ADD COLUMN billing_manager_assigned_by UUID REFERENCES users(id);

CREATE INDEX idx_patients_billing_manager ON patients(billing_manager_id) WHERE billing_manager_id IS NOT NULL;

-- Create billing transactions table
CREATE TABLE billing_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL,
    owner_type VARCHAR(20) NOT NULL CHECK (owner_type IN ('PATIENT', 'ORGANIZATION')),
    stripe_payment_intent_id VARCHAR(100) UNIQUE,
    stripe_invoice_id VARCHAR(100),
    stripe_charge_id VARCHAR(100),
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'usd',
    status VARCHAR(20) NOT NULL CHECK (status IN ('SUCCEEDED', 'FAILED', 'REFUNDED', 'PENDING', 'CANCELLED')),
    description TEXT,
    receipt_url VARCHAR(500),
    receipt_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    refunded_at TIMESTAMP WITH TIME ZONE,
    refunded_by UUID REFERENCES users(id),
    refund_reason TEXT,
    managed_by_proxy_id UUID REFERENCES users(id),  -- Proxy who initiated transaction
    metadata JSONB
);

CREATE INDEX idx_billing_transactions_owner ON billing_transactions(owner_id, owner_type);
CREATE INDEX idx_billing_transactions_status ON billing_transactions(status);
CREATE INDEX idx_billing_transactions_created ON billing_transactions(created_at DESC);
CREATE INDEX idx_billing_transactions_stripe_pi ON billing_transactions(stripe_payment_intent_id);
CREATE INDEX idx_billing_transactions_proxy ON billing_transactions(managed_by_proxy_id) WHERE managed_by_proxy_id IS NOT NULL;

CREATE TABLE subscription_overrides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL,
    owner_type VARCHAR(20) NOT NULL CHECK (owner_type IN ('PATIENT', 'ORGANIZATION')),
    override_type VARCHAR(30) NOT NULL CHECK (override_type IN ('FREE', 'TRIAL_EXTENSION', 'MANUAL_CANCEL', 'DISCOUNT')),
    granted_by UUID NOT NULL REFERENCES users(id),
    reason TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    discount_percent INTEGER CHECK (discount_percent >= 0 AND discount_percent <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by UUID REFERENCES users(id),
    metadata JSONB
);

CREATE INDEX idx_subscription_overrides_owner ON subscription_overrides(owner_id, owner_type);
CREATE INDEX idx_subscription_overrides_active ON subscription_overrides(owner_id, owner_type)
    WHERE revoked_at IS NULL;
```

#### 2. Models: `backend/src/models/billing.py` (NEW)
```python
from sqlalchemy import Column, String, Integer, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base

class BillingTransaction(Base):
    __tablename__ = "billing_transactions"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    owner_type: Mapped[str] = mapped_column(String(20), nullable=False)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    stripe_invoice_id: Mapped[str | None] = mapped_column(String(100))
    stripe_charge_id: Mapped[str | None] = mapped_column(String(100))
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd")
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    receipt_url: Mapped[str | None] = mapped_column(String(500))
    receipt_number: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    refunded_at: Mapped[datetime | None]
    refunded_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    refund_reason: Mapped[str | None] = mapped_column(Text)
    metadata: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        CheckConstraint("owner_type IN ('PATIENT', 'ORGANIZATION')"),
        CheckConstraint("status IN ('SUCCEEDED', 'FAILED', 'REFUNDED', 'PENDING', 'CANCELLED')"),
        Index("idx_billing_transactions_owner", "owner_id", "owner_type"),
        Index("idx_billing_transactions_status", "status"),
        Index("idx_billing_transactions_created", "created_at"),
    )

class SubscriptionOverride(Base):
    __tablename__ = "subscription_overrides"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    owner_type: Mapped[str] = mapped_column(String(20), nullable=False)
    override_type: Mapped[str] = mapped_column(String(30), nullable=False)
    granted_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None]
    discount_percent: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime]
    revoked_at: Mapped[datetime | None]
    revoked_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    metadata: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        CheckConstraint("owner_type IN ('PATIENT', 'ORGANIZATION')"),
        CheckConstraint("override_type IN ('FREE', 'TRIAL_EXTENSION', 'MANUAL_CANCEL', 'DISCOUNT')"),
        CheckConstraint("discount_percent >= 0 AND discount_percent <= 100"),
        Index("idx_subscription_overrides_owner", "owner_id", "owner_type"),
    )
```

#### 3. Schemas: `backend/src/schemas/billing.py` (EXTEND)
```python
# Add to existing billing.py

class BillingTransactionResponse(BaseModel):
    id: UUID
    amount_cents: int
    currency: str
    status: str
    description: str | None
    receipt_url: str | None
    receipt_number: str | None
    created_at: datetime
    refunded_at: datetime | None
    refund_reason: str | None

class TransactionListResponse(BaseModel):
    transactions: list[BillingTransactionResponse]
    total: int
    page: int
    page_size: int

class CancelSubscriptionRequest(BaseModel):
    reason: str | None = None
    cancel_immediately: bool = False  # If True, cancel now; if False, at period end

class CancelSubscriptionResponse(BaseModel):
    success: bool
    cancelled_at: datetime | None
    cancels_at_period_end: bool
    message: str
```

#### 4. Service Extension: `backend/src/services/billing.py` (EXTEND)
```python
# Add patient-specific methods

async def get_or_create_patient_customer(
    patient_id: str,
    db: AsyncSession
) -> str:
    """Get or create Stripe customer for patient"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise ValueError("Patient not found")

    if patient.stripe_customer_id:
        return patient.stripe_customer_id

    # Create Stripe customer
    customer_id = await create_customer(
        owner_id=patient_id,
        owner_type=CustomerType.PATIENT,
        email=patient.email,
        name=f"{patient.first_name} {patient.last_name}"
    )

    patient.stripe_customer_id = customer_id
    await db.commit()
    return customer_id

async def cancel_subscription(
    customer_id: str,
    cancel_immediately: bool = False
) -> dict:
    """Cancel a Stripe subscription"""
    subscriptions = stripe.Subscription.list(
        customer=customer_id,
        status="active",
        limit=1
    )

    if not subscriptions.data:
        raise ValueError("No active subscription found")

    subscription = subscriptions.data[0]

    if cancel_immediately:
        cancelled = stripe.Subscription.cancel(subscription.id)
    else:
        cancelled = stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=True
        )

    return {
        "subscription_id": cancelled.id,
        "status": cancelled.status,
        "cancelled_at": cancelled.canceled_at,
        "cancels_at_period_end": cancelled.cancel_at_period_end
    }

async def record_transaction(
    db: AsyncSession,
    owner_id: str,
    owner_type: str,
    stripe_payment_intent_id: str | None,
    stripe_invoice_id: str | None,
    stripe_charge_id: str | None,
    amount_cents: int,
    currency: str,
    status: str,
    description: str | None = None,
    receipt_url: str | None = None,
    receipt_number: str | None = None,
    metadata: dict | None = None
) -> BillingTransaction:
    """Record a billing transaction in database"""
    transaction = BillingTransaction(
        owner_id=owner_id,
        owner_type=owner_type,
        stripe_payment_intent_id=stripe_payment_intent_id,
        stripe_invoice_id=stripe_invoice_id,
        stripe_charge_id=stripe_charge_id,
        amount_cents=amount_cents,
        currency=currency,
        status=status,
        description=description,
        receipt_url=receipt_url,
        receipt_number=receipt_number,
        metadata=metadata
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction
```

#### 5. API Router: `backend/src/api/patients_billing.py` (NEW)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.profiles import Patient
from ..models.billing import BillingTransaction
from ..services import billing as billing_service
from ..schemas.billing import *
from ..auth import get_current_user, User

router = APIRouter()

@router.post("/{patient_id}/billing/checkout", response_model=CheckoutSessionResponse)
async def create_patient_checkout(
    patient_id: str,
    request: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create checkout session for patient subscription"""
    # Verify access: user must be the patient or staff
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    if current_user.id != patient.user_id:
        # Check if user is staff in patient's organization
        # (Add org staff check here)
        raise HTTPException(403, "Not authorized")

    # Get or create Stripe customer
    customer_id = await billing_service.get_or_create_patient_customer(patient_id, db)

    # Create checkout session
    session = await billing_service.create_checkout_session(
        customer_id=customer_id,
        price_id=request.price_id,
        success_url=f"{settings.FRONTEND_URL}/patient/billing/success",
        cancel_url=f"{settings.FRONTEND_URL}/patient/billing"
    )

    return session

@router.get("/{patient_id}/billing/subscription", response_model=SubscriptionStatus)
async def get_patient_subscription(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get patient's current subscription status"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    if current_user.id != patient.user_id:
        # Check if user is staff
        raise HTTPException(403, "Not authorized")

    if not patient.stripe_customer_id:
        return SubscriptionStatus(status="NONE")

    return await billing_service.get_subscription_status(patient.stripe_customer_id)

@router.post("/{patient_id}/billing/portal", response_model=PortalSessionResponse)
async def create_patient_portal(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create billing portal session for patient"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    if current_user.id != patient.user_id:
        raise HTTPException(403, "Not authorized")

    if not patient.stripe_customer_id:
        raise HTTPException(400, "No billing account found")

    return await billing_service.create_portal_session(
        customer_id=patient.stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/patient/billing"
    )

@router.get("/{patient_id}/billing/transactions", response_model=TransactionListResponse)
async def get_patient_transactions(
    patient_id: str,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get patient's billing transaction history"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    if current_user.id != patient.user_id:
        raise HTTPException(403, "Not authorized")

    # Query transactions
    offset = (page - 1) * page_size
    query = select(BillingTransaction).where(
        BillingTransaction.owner_id == patient_id,
        BillingTransaction.owner_type == "PATIENT"
    ).order_by(BillingTransaction.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    transactions = result.scalars().all()

    # Get total count
    count_query = select(func.count()).select_from(BillingTransaction).where(
        BillingTransaction.owner_id == patient_id,
        BillingTransaction.owner_type == "PATIENT"
    )
    total = await db.scalar(count_query)

    return TransactionListResponse(
        transactions=[BillingTransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size
    )

@router.post("/{patient_id}/billing/cancel", response_model=CancelSubscriptionResponse)
async def cancel_patient_subscription(
    patient_id: str,
    request: CancelSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel patient's subscription"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    if current_user.id != patient.user_id:
        raise HTTPException(403, "Not authorized")

    if not patient.stripe_customer_id:
        raise HTTPException(400, "No active subscription")

    try:
        result = await billing_service.cancel_subscription(
            customer_id=patient.stripe_customer_id,
            cancel_immediately=request.cancel_immediately
        )

        return CancelSubscriptionResponse(
            success=True,
            cancelled_at=datetime.fromtimestamp(result["cancelled_at"]) if result["cancelled_at"] else None,
            cancels_at_period_end=result["cancels_at_period_end"],
            message="Subscription cancelled successfully"
        )
    except Exception as e:
        raise HTTPException(400, str(e))
```

#### 6. Router Registration: `backend/src/main.py` (EXTEND)
```python
from .api import patients_billing

app.include_router(
    patients_billing.router,
    prefix=f"{settings.API_V1_STR}/patients",
    tags=["patient-billing"]
)
```

#### 7. Webhook Enhancement: `backend/src/api/webhooks.py` (EXTEND)
```python
# Update webhook handlers to record transactions

async def _handle_payment_succeeded(event: dict) -> WebhookResult:
    """Handle successful payment"""
    invoice = event["data"]["object"]
    customer_id = invoice["customer"]

    # Existing status update logic...

    # NEW: Record transaction
    owner_id, owner_type = await _get_owner_from_customer(customer_id, db)
    if owner_id:
        await billing_service.record_transaction(
            db=db,
            owner_id=owner_id,
            owner_type=owner_type,
            stripe_payment_intent_id=invoice.get("payment_intent"),
            stripe_invoice_id=invoice["id"],
            stripe_charge_id=invoice.get("charge"),
            amount_cents=invoice["amount_paid"],
            currency=invoice["currency"],
            status="SUCCEEDED",
            description=f"Subscription payment - {invoice.get('lines', {}).get('data', [{}])[0].get('description')}",
            receipt_url=invoice.get("hosted_invoice_url"),
            receipt_number=invoice.get("number")
        )

    return WebhookResult(...)

# Similar updates for _handle_payment_failed
```

## Acceptance Criteria
### Database & Models
- [ ] `billing_transactions` table created with all fields and indexes including `managed_by_proxy_id`.
- [ ] `subscription_overrides` table created.
- [ ] Patient model extended with `billing_manager_id`, `billing_manager_assigned_at`, `billing_manager_assigned_by`.
- [ ] `BillingTransaction` and `SubscriptionOverride` models defined.
- [ ] Indexes created for billing manager queries.

### Patient Billing Endpoints
- [ ] Patient can create checkout session via `POST /patients/{id}/billing/checkout`.
- [ ] Patient can view subscription status via `GET /patients/{id}/billing/subscription`.
- [ ] Patient can access billing portal via `POST /patients/{id}/billing/portal`.
- [ ] Patient can view transaction history via `GET /patients/{id}/billing/transactions`.
- [ ] Patient can cancel subscription via `POST /patients/{id}/billing/cancel`.

### Billing Manager Assignment
- [ ] Patient can assign billing manager via `PUT /patients/{id}/billing/manager`.
- [ ] Patient can remove billing manager via `DELETE /patients/{id}/billing/manager`.
- [ ] Assignment validates active proxy relationship exists.
- [ ] Assignment records who assigned and when.

### Proxy Billing Endpoints
- [ ] Proxy can list all managed patients via `GET /proxy/managed-patients/billing`.
- [ ] Proxy can view patient subscription via `GET /proxy/managed-patients/{id}/billing/subscription`.
- [ ] Proxy can create checkout for patient via `POST /proxy/managed-patients/{id}/billing/checkout`.
- [ ] Proxy can view patient transactions via `GET /proxy/managed-patients/{id}/billing/transactions`.
- [ ] Proxy can cancel patient subscription via `POST /proxy/managed-patients/{id}/billing/cancel`.

### Access Control
- [ ] Access control enforced: patient, billing manager, or staff can access.
- [ ] Proxy must have active proxy relationship to be billing manager.
- [ ] `can_manage_billing()` helper validates access correctly.
- [ ] Unauthorized users receive 403 errors.

### System Requirements
- [ ] Webhook handlers record all transactions in database.
- [ ] Transactions record `managed_by_proxy_id` when proxy initiates.
- [ ] Audit log captures all billing API calls with actor ID.
- [ ] Audit log captures billing manager assignments/removals.

## Verification Plan
**Automated Tests:**
```bash
pytest tests/api/test_patients_billing.py -v
pytest tests/services/test_billing.py -v
```

**Test Cases:**
1. Test patient checkout session creation
2. Test transaction recording on webhook
3. Test access control (patient vs other user)
4. Test subscription cancellation (immediate vs end of period)
5. Test transaction pagination

**Manual Verification:**
1. Run migration: `alembic upgrade head`
2. Create patient checkout session
3. Complete payment in Stripe test mode
4. Verify transaction recorded in database
5. View transaction history
6. Cancel subscription
7. Verify cancellation in Stripe and database

## Security Considerations
- [ ] Validate patient_id matches current_user
- [ ] Rate limit billing endpoints (max 10 requests/minute per user)
- [ ] Sanitize all user inputs
- [ ] Log all billing actions to audit table
- [ ] Never expose Stripe customer IDs to frontend
- [ ] Validate all Stripe webhook signatures

## Rollback Plan
If issues arise:
1. Disable patient billing endpoints via feature flag
2. Roll back database migration if no data corruption
3. Keep webhook handlers active to maintain org billing
4. Investigate and fix issues in staging environment
