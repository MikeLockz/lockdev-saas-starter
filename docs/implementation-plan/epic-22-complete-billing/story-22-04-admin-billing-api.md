# Story 22.4: Admin Billing Management API
**User Story:** As an Admin, I want API endpoints to manage all user subscriptions, issue refunds, grant free subscriptions, and manage billing manager assignments, so that I can handle billing support cases.

## Status
- [x] **Complete**

## Context
- **Epic:** Epic 22 - Complete Billing & Subscription Management
- **Dependencies:**
  - Story 22.1 (Patient Billing API) - includes billing manager model
- **Existing Code:**
  - `backend/src/api/billing.py` - Organization billing
  - `backend/src/models/billing.py` - Billing models with billing_manager_id
  - `backend/src/services/billing.py` - Billing service

## Billing Manager Management Requirements
**Key Feature:** Admins can view, assign, and remove billing managers for any patient.

- View all billing manager relationships across system
- Assign billing manager without proxy relationship requirement (admin override)
- Remove billing manager assignments
- Audit all billing manager changes

## Technical Specification
**Goal:** Build admin API endpoints for comprehensive billing management including billing manager oversight.

### Changes Required

#### 1. Schemas: `backend/src/schemas/admin_billing.py` (NEW)
```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class SubscriptionListFilter(BaseModel):
    status: str | None = None  # ACTIVE, CANCELED, PAST_DUE, etc.
    owner_type: str | None = None  # PATIENT, ORGANIZATION
    search: str | None = None  # Search by name, email
    date_from: datetime | None = None
    date_to: datetime | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)

class SubscriptionListItem(BaseModel):
    owner_id: UUID
    owner_type: str
    owner_name: str
    owner_email: str
    stripe_customer_id: str
    subscription_status: str
    plan_id: str | None
    current_period_end: datetime | None
    mrr_cents: int  # Monthly Recurring Revenue
    created_at: datetime
    cancelled_at: datetime | None
    billing_manager_id: UUID | None  # NEW
    billing_manager_name: str | None  # NEW

class BillingManagerRelationship(BaseModel):
    """Billing manager relationship details"""
    patient_id: UUID
    patient_name: str
    patient_email: str
    billing_manager_id: UUID
    billing_manager_name: str
    billing_manager_email: str
    assigned_at: datetime
    assigned_by: UUID
    assigned_by_name: str

class AssignBillingManagerRequest(BaseModel):
    proxy_user_id: UUID

class RemoveBillingManagerResponse(BaseModel):
    success: bool
    message: str

class SubscriptionListResponse(BaseModel):
    subscriptions: list[SubscriptionListItem]
    total: int
    page: int
    page_size: int
    total_mrr_cents: int

class RefundRequest(BaseModel):
    transaction_id: UUID
    amount_cents: int | None = None  # Partial refund if specified
    reason: str

class RefundResponse(BaseModel):
    success: bool
    refund_id: str
    amount_refunded_cents: int
    message: str

class GrantFreeSubscriptionRequest(BaseModel):
    owner_id: UUID
    owner_type: str  # PATIENT or ORGANIZATION
    reason: str
    duration_months: int | None = None  # None = indefinite

class GrantFreeSubscriptionResponse(BaseModel):
    success: bool
    override_id: UUID
    message: str

class BillingAnalytics(BaseModel):
    total_active_subscriptions: int
    total_mrr_cents: int
    new_subscriptions_this_month: int
    cancelled_subscriptions_this_month: int
    churn_rate: float
    average_revenue_per_user_cents: int
    failed_payments_this_month: int
    total_revenue_this_month_cents: int

class ManualCancelRequest(BaseModel):
    reason: str
    cancel_immediately: bool = False
    refund_remaining: bool = False
```

#### 2. Service Extension: `backend/src/services/billing.py` (EXTEND)
```python
# Add admin-specific billing functions

async def get_all_subscriptions(
    db: AsyncSession,
    filters: SubscriptionListFilter
) -> tuple[list[SubscriptionListItem], int]:
    """Get all subscriptions with filters"""
    # Build query combining org and patient subscriptions
    query = """
        SELECT
            owner_id,
            owner_type,
            owner_name,
            owner_email,
            stripe_customer_id,
            subscription_status,
            plan_id,
            current_period_end,
            mrr_cents,
            created_at,
            cancelled_at
        FROM (
            SELECT
                o.id as owner_id,
                'ORGANIZATION' as owner_type,
                o.name as owner_name,
                u.email as owner_email,
                o.stripe_customer_id,
                o.subscription_status,
                NULL as plan_id,  -- Get from Stripe
                NULL as current_period_end,
                0 as mrr_cents,  -- Calculate from Stripe
                o.created_at,
                NULL as cancelled_at
            FROM organizations o
            JOIN organization_members om ON o.id = om.organization_id AND om.role = 'ADMIN'
            JOIN users u ON om.user_id = u.id
            WHERE o.stripe_customer_id IS NOT NULL

            UNION ALL

            SELECT
                p.id as owner_id,
                'PATIENT' as owner_type,
                CONCAT(p.first_name, ' ', p.last_name) as owner_name,
                p.email as owner_email,
                p.stripe_customer_id,
                p.subscription_status,
                NULL as plan_id,
                NULL as current_period_end,
                0 as mrr_cents,
                p.created_at,
                NULL as cancelled_at
            FROM patients p
            WHERE p.stripe_customer_id IS NOT NULL
        ) combined
        WHERE 1=1
    """

    # Apply filters
    conditions = []
    params = {}

    if filters.status:
        conditions.append("subscription_status = :status")
        params["status"] = filters.status

    if filters.owner_type:
        conditions.append("owner_type = :owner_type")
        params["owner_type"] = filters.owner_type

    if filters.search:
        conditions.append("(owner_name ILIKE :search OR owner_email ILIKE :search)")
        params["search"] = f"%{filters.search}%"

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"
    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = filters.page_size
    params["offset"] = (filters.page - 1) * filters.page_size

    result = await db.execute(text(query), params)
    subscriptions = result.fetchall()

    # Get total count
    count_query = query.split("ORDER BY")[0]
    total = await db.scalar(text(f"SELECT COUNT(*) FROM ({count_query}) cnt"), params)

    return subscriptions, total

async def refund_transaction(
    db: AsyncSession,
    transaction_id: UUID,
    amount_cents: int | None,
    reason: str,
    refunded_by: UUID
) -> dict:
    """Refund a transaction (full or partial)"""
    transaction = await db.get(BillingTransaction, transaction_id)
    if not transaction:
        raise ValueError("Transaction not found")

    if transaction.status == "REFUNDED":
        raise ValueError("Transaction already refunded")

    if not transaction.stripe_payment_intent_id:
        raise ValueError("No Stripe payment intent ID")

    # Refund via Stripe
    refund_amount = amount_cents or transaction.amount_cents

    refund = stripe.Refund.create(
        payment_intent=transaction.stripe_payment_intent_id,
        amount=refund_amount,
        reason="requested_by_customer",
        metadata={"reason": reason}
    )

    # Update transaction
    transaction.status = "REFUNDED"
    transaction.refunded_at = datetime.utcnow()
    transaction.refunded_by = refunded_by
    transaction.refund_reason = reason

    await db.commit()

    return {
        "refund_id": refund.id,
        "amount_refunded": refund_amount
    }

async def grant_free_subscription(
    db: AsyncSession,
    owner_id: UUID,
    owner_type: str,
    reason: str,
    granted_by: UUID,
    duration_months: int | None = None
) -> SubscriptionOverride:
    """Grant free subscription to user"""
    # Create override
    expires_at = None
    if duration_months:
        expires_at = datetime.utcnow() + timedelta(days=duration_months * 30)

    override = SubscriptionOverride(
        owner_id=owner_id,
        owner_type=owner_type,
        override_type="FREE",
        granted_by=granted_by,
        reason=reason,
        expires_at=expires_at
    )

    db.add(override)

    # Cancel existing Stripe subscription if any
    if owner_type == "PATIENT":
        patient = await db.get(Patient, owner_id)
        if patient and patient.stripe_customer_id:
            await cancel_subscription(patient.stripe_customer_id, cancel_immediately=True)
    else:
        org = await db.get(Organization, owner_id)
        if org and org.stripe_customer_id:
            await cancel_subscription(org.stripe_customer_id, cancel_immediately=True)

    await db.commit()
    await db.refresh(override)

    return override

async def calculate_billing_analytics(db: AsyncSession) -> BillingAnalytics:
    """Calculate billing analytics"""
    # Complex queries to calculate metrics
    # This is a simplified version
    total_active = await db.scalar(
        select(func.count()).select_from(Patient).where(
            Patient.subscription_status.in_(["ACTIVE", "TRIALING"])
        )
    )

    # Get Stripe data for accurate MRR
    # Calculate churn, revenue, etc.

    return BillingAnalytics(
        total_active_subscriptions=total_active,
        total_mrr_cents=0,  # Calculate from Stripe
        new_subscriptions_this_month=0,
        cancelled_subscriptions_this_month=0,
        churn_rate=0.0,
        average_revenue_per_user_cents=0,
        failed_payments_this_month=0,
        total_revenue_this_month_cents=0
    )
```

#### 3. API Router: `backend/src/api/admin_billing.py` (NEW)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..auth import get_current_user, User, require_super_admin
from ..schemas.admin_billing import *
from ..services import billing as billing_service

router = APIRouter()

@router.get("/billing/subscriptions", response_model=SubscriptionListResponse)
async def list_all_subscriptions(
    filters: SubscriptionListFilter = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Get all subscriptions across all customers (admin only)"""
    subscriptions, total = await billing_service.get_all_subscriptions(db, filters)

    # Calculate total MRR
    total_mrr = sum(sub.mrr_cents for sub in subscriptions)

    return SubscriptionListResponse(
        subscriptions=subscriptions,
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_mrr_cents=total_mrr
    )

@router.post("/billing/transactions/{transaction_id}/refund", response_model=RefundResponse)
async def refund_transaction(
    transaction_id: UUID,
    request: RefundRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Refund a transaction (full or partial)"""
    try:
        result = await billing_service.refund_transaction(
            db=db,
            transaction_id=request.transaction_id,
            amount_cents=request.amount_cents,
            reason=request.reason,
            refunded_by=current_user.id
        )

        return RefundResponse(
            success=True,
            refund_id=result["refund_id"],
            amount_refunded_cents=result["amount_refunded"],
            message="Refund processed successfully"
        )
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/billing/grant-free", response_model=GrantFreeSubscriptionResponse)
async def grant_free_subscription(
    request: GrantFreeSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Grant free subscription to a user"""
    try:
        override = await billing_service.grant_free_subscription(
            db=db,
            owner_id=request.owner_id,
            owner_type=request.owner_type,
            reason=request.reason,
            granted_by=current_user.id,
            duration_months=request.duration_months
        )

        return GrantFreeSubscriptionResponse(
            success=True,
            override_id=override.id,
            message=f"Free subscription granted for {request.duration_months or 'unlimited'} months"
        )
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/billing/analytics", response_model=BillingAnalytics)
async def get_billing_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Get billing analytics (admin only)"""
    return await billing_service.calculate_billing_analytics(db)

@router.post("/billing/subscriptions/{owner_type}/{owner_id}/cancel", response_model=CancelSubscriptionResponse)
async def admin_cancel_subscription(
    owner_type: str,
    owner_id: UUID,
    request: ManualCancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Admin manually cancels a user's subscription"""
    # Get customer
    if owner_type == "PATIENT":
        owner = await db.get(Patient, owner_id)
    else:
        owner = await db.get(Organization, owner_id)

    if not owner or not owner.stripe_customer_id:
        raise HTTPException(404, "Customer not found")

    result = await billing_service.cancel_subscription(
        customer_id=owner.stripe_customer_id,
        cancel_immediately=request.cancel_immediately
    )

    # Log admin action
    # Send notification to user

    return CancelSubscriptionResponse(
        success=True,
        cancelled_at=datetime.fromtimestamp(result["cancelled_at"]) if result["cancelled_at"] else None,
        cancels_at_period_end=result["cancels_at_period_end"],
        message="Subscription cancelled by admin"
    )

@router.get("/billing/transactions", response_model=TransactionListResponse)
async def list_all_transactions(
    page: int = 1,
    page_size: int = 50,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Get all transactions across all customers (admin only)"""
    offset = (page - 1) * page_size

    query = select(BillingTransaction).order_by(
        BillingTransaction.created_at.desc()
    )

    if status:
        query = query.where(BillingTransaction.status == status)

    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    transactions = result.scalars().all()

    # Get total count
    count_query = select(func.count()).select_from(BillingTransaction)
    if status:
        count_query = count_query.where(BillingTransaction.status == status)
    total = await db.scalar(count_query)

    return TransactionListResponse(
        transactions=[BillingTransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size
    )

# NEW: Billing Manager Management Endpoints

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
        assigner = await db.get(User, patient.billing_manager_assigned_by)

        relationships.append(BillingManagerRelationship(
            patient_id=patient.id,
            patient_name=f"{patient.first_name} {patient.last_name}",
            patient_email=patient.email,
            billing_manager_id=patient.billing_manager_id,
            billing_manager_name=f"{manager.first_name} {manager.last_name}",
            billing_manager_email=manager.email,
            assigned_at=patient.billing_manager_assigned_at,
            assigned_by=patient.billing_manager_assigned_by,
            assigned_by_name=f"{assigner.first_name} {assigner.last_name}" if assigner else "Unknown"
        ))

    return relationships

@router.put("/patients/{patient_id}/billing/manager")
async def admin_assign_billing_manager(
    patient_id: UUID,
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

    return {"success": True, "message": "Billing manager assigned by admin"}

@router.delete("/patients/{patient_id}/billing/manager")
async def admin_remove_billing_manager(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Admin removes billing manager"""
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    patient.billing_manager_id = None
    patient.billing_manager_assigned_at = None
    patient.billing_manager_assigned_by = None

    await db.commit()

    return RemoveBillingManagerResponse(
        success=True,
        message="Billing manager removed by admin"
    )
```

#### 4. Router Registration: `backend/src/main.py` (EXTEND)
```python
from .api import admin_billing

app.include_router(
    admin_billing.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["admin-billing"]
)
```

#### 5. Permissions: `backend/src/auth.py` (EXTEND)
```python
async def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require super admin role"""
    if not current_user.is_super_admin:
        raise HTTPException(403, "Super admin access required")
    return current_user
```

## Acceptance Criteria
###Subscription Management
- [ ] Admin can list all subscriptions with pagination and filters.
- [ ] Subscription list includes billing_manager_id and billing_manager_name.
- [ ] Admin can search subscriptions by name or email.
- [ ] Admin can refund transactions (full or partial).
- [ ] Admin can grant free subscriptions to users.
- [ ] Admin can manually cancel any subscription.
- [ ] Admin can view billing analytics dashboard.
- [ ] Admin can view all transactions across all customers.

### Billing Manager Management
- [ ] Admin can list all billing manager relationships via `GET /billing/managers`.
- [ ] List shows patient name, manager name, assigned date, and assigner.
- [ ] Admin can assign billing manager via `PUT /patients/{id}/billing/manager`.
- [ ] Admin assignment bypasses proxy relationship requirement.
- [ ] Admin can remove billing manager via `DELETE /patients/{id}/billing/manager`.
- [ ] Billing manager changes logged with admin user ID.

### Security & Audit
- [ ] All admin actions logged in audit trail with actor ID.
- [ ] Only super admins can access endpoints (403 for others).
- [ ] Refunds reflect immediately in Stripe and database.
- [ ] Billing manager assignments/removals trigger audit events.

## Verification Plan
**Automated Tests:**
```bash
pytest tests/api/test_admin_billing.py -v
```

**Test Cases:**
1. Test subscription list with various filters
2. Test refund (full and partial)
3. Test grant free subscription
4. Test admin cancel subscription
5. Test analytics calculation
6. Test access control (non-admin user gets 403)
7. Test search functionality
8. Test list billing managers endpoint
9. Test admin assign billing manager (bypasses proxy check)
10. Test admin remove billing manager
11. Test subscription list shows billing manager info

**Manual Verification:**
1. Login as super admin
2. View subscriptions list
3. Issue a refund
4. Grant free subscription to test user
5. View analytics dashboard
6. Cancel a subscription
7. View all billing manager relationships
8. Assign billing manager to a patient
9. Remove billing manager from a patient
10. Verify all in Stripe dashboard

## Security Considerations
- [ ] Require super admin role for all endpoints
- [ ] Log all admin actions with actor ID
- [ ] Rate limit admin endpoints
- [ ] Validate all input parameters
- [ ] Prevent accidental mass refunds
- [ ] Require confirmation for destructive actions
- [ ] Audit all data access

## Rollback Plan
If issues arise:
1. Disable admin billing endpoints via feature flag
2. Use Stripe dashboard for manual operations
3. Review and fix issues in staging
4. Re-enable gradually with monitoring
