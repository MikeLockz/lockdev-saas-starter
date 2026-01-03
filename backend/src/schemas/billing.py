"""
Billing Schemas

Pydantic models for billing API requests and responses.
"""

from pydantic import BaseModel


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
