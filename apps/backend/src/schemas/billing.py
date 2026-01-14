"""
Billing Schemas

Pydantic models for billing API requests and responses.
Epic 22 - Complete Billing & Subscription Management
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CheckoutSessionRequest(BaseModel):
    """Request to create a Stripe checkout session."""

    price_id: str


class CheckoutSessionResponse(BaseModel):
    """Response from creating a checkout session."""

    session_id: str
    checkout_url: str


class SubscriptionStatusResponse(BaseModel):
    """Current subscription status for an organization."""

    status: str
    plan_id: str | None = None
    current_period_end: int | None = None
    cancel_at_period_end: bool = False


class PortalSessionResponse(BaseModel):
    """Response from creating a billing portal session."""

    portal_url: str


# ============================================================================
# PATIENT BILLING SCHEMAS (Epic 22)
# ============================================================================


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel a subscription."""

    cancel_immediately: bool = Field(
        default=False,
        description="If True, cancel immediately; if False, cancel at period end",
    )
    reason: str | None = Field(default=None, description="Optional cancellation reason")


class TransactionResponse(BaseModel):
    """Billing transaction response."""

    id: UUID
    owner_id: UUID
    owner_type: str
    amount_cents: int
    currency: str
    status: str
    description: str | None
    receipt_url: str | None
    receipt_number: str | None
    created_at: datetime
    managed_by_proxy_id: UUID | None = None

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """List of billing transactions."""

    transactions: list[TransactionResponse]
    total: int


class SubscriptionOverrideResponse(BaseModel):
    """Subscription override response."""

    id: UUID
    owner_id: UUID
    owner_type: str
    override_type: str
    reason: str
    granted_by: UUID
    expires_at: datetime | None
    discount_percent: int | None
    created_at: datetime
    revoked_at: datetime | None

    class Config:
        from_attributes = True


class GrantFreeSubscriptionRequest(BaseModel):
    """Request to grant a free subscription."""

    owner_id: UUID
    owner_type: str = Field(pattern="^(PATIENT|ORGANIZATION)$")
    reason: str = Field(min_length=10, description="Reason for granting free subscription")
    duration_months: int | None = Field(
        default=None,
        ge=1,
        le=120,
        description="Duration in months (None for indefinite)",
    )


class RefundTransactionRequest(BaseModel):
    """Request to refund a transaction."""

    transaction_id: UUID
    amount_cents: int | None = Field(
        default=None,
        description="Amount to refund in cents (None for full refund)",
    )
    reason: str = Field(min_length=5, description="Reason for refund")


class AssignBillingManagerRequest(BaseModel):
    """Request to assign a billing manager to a patient."""

    proxy_user_id: UUID = Field(description="User ID of the proxy to assign as billing manager")


class BillingManagerResponse(BaseModel):
    """Billing manager assignment response."""

    patient_id: UUID
    patient_name: str
    billing_manager_id: UUID
    billing_manager_name: str
    billing_manager_email: str
    assigned_at: datetime
    assigned_by: UUID | None


class BillingManagerListResponse(BaseModel):
    """List of billing manager relationships."""

    relationships: list[BillingManagerResponse]
    total: int


# ============================================================================
# ADMIN BILLING SCHEMAS (Story 22.4)
# ============================================================================


class SubscriptionListFilter(BaseModel):
    """Filter parameters for listing subscriptions."""

    status: str | None = Field(default=None, description="Subscription status filter")
    owner_type: str | None = Field(default=None, pattern="^(PATIENT|ORGANIZATION)$")
    search: str | None = Field(default=None, description="Search by name or email")
    date_from: datetime | None = None
    date_to: datetime | None = None


class SubscriptionListItem(BaseModel):
    """Subscription details for admin list view."""

    owner_id: UUID
    owner_type: str
    owner_name: str
    owner_email: str | None
    stripe_customer_id: str | None
    subscription_status: str | None
    plan_id: str | None = None
    current_period_end: datetime | None = None
    mrr_cents: int = 0
    created_at: datetime
    cancelled_at: datetime | None = None
    billing_manager_id: UUID | None = None
    billing_manager_name: str | None = None


class SubscriptionListResponse(BaseModel):
    """Paginated subscription list response."""

    subscriptions: list[SubscriptionListItem]
    total: int
    page: int
    page_size: int
    total_mrr_cents: int = 0


class BillingAnalytics(BaseModel):
    """Billing analytics summary."""

    total_active_subscriptions: int
    total_mrr_cents: int
    new_subscriptions_this_month: int
    cancelled_subscriptions_this_month: int
    churn_rate: float
    average_revenue_per_user_cents: int
    failed_payments_this_month: int
    total_revenue_this_month_cents: int


class ManualCancelRequest(BaseModel):
    """Admin request to manually cancel a subscription."""

    reason: str = Field(min_length=5, description="Reason for cancellation")
    cancel_immediately: bool = Field(
        default=False,
        description="If True, cancel immediately; if False, cancel at period end",
    )
    refund_remaining: bool = Field(
        default=False,
        description="If True, refund remaining pro-rated amount",
    )


class CancelSubscriptionResponse(BaseModel):
    """Response after cancelling a subscription."""

    success: bool
    cancelled_at: datetime | None = None
    cancels_at_period_end: bool = False
    message: str


class RefundResponse(BaseModel):
    """Response after processing a refund."""

    success: bool
    refund_id: str
    amount_refunded_cents: int
    message: str
