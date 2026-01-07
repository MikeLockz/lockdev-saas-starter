"""
Stripe Billing Service

This module handles Stripe subscription management for Organizations and Patients.
"""

import logging
from enum import Enum
from typing import Any

import stripe
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_API_KEY


class CustomerType(str, Enum):
    """Type of Stripe customer."""

    ORGANIZATION = "ORG"
    PATIENT = "PATIENT"


class CheckoutSessionResponse(BaseModel):
    """Response from creating a checkout session."""

    checkout_url: str
    session_id: str


class PortalSessionResponse(BaseModel):
    """Response from creating a billing portal session."""

    portal_url: str


class WebhookResult(BaseModel):
    """Result of processing a webhook event."""

    success: bool
    event_type: str
    customer_id: str | None = None
    subscription_status: str | None = None
    message: str | None = None


async def create_customer(
    owner_id: str,
    owner_type: CustomerType,
    email: str,
    name: str,
) -> str:
    """
    Create a Stripe Customer for an Organization or Patient.

    Args:
        owner_id: The ID of the organization or patient
        owner_type: Whether this is an ORG or PATIENT customer
        email: Customer email address
        name: Customer name (org name or patient name)

    Returns:
        Stripe customer ID (cus_...)
    """
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                "owner_id": owner_id,
                "owner_type": owner_type.value,
            },
        )
        logger.info(
            "Created Stripe customer",
            extra={
                "customer_id": customer.id,
                "owner_id": owner_id,
                "owner_type": owner_type.value,
            },
        )
        return customer.id
    except stripe.StripeError as e:
        logger.error(f"Failed to create Stripe customer: {e}")
        raise


async def create_checkout_session(
    customer_id: str,
    price_id: str,
    success_url: str | None = None,
    cancel_url: str | None = None,
) -> CheckoutSessionResponse:
    """
    Create a Stripe Checkout Session for subscription.

    Args:
        customer_id: Stripe customer ID (cus_...)
        price_id: Stripe price ID for the subscription plan
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if user cancels

    Returns:
        CheckoutSessionResponse with URL and session ID
    """
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            success_url=success_url or settings.STRIPE_SUCCESS_URL,
            cancel_url=cancel_url or settings.STRIPE_CANCEL_URL,
        )
        logger.info(
            "Created checkout session",
            extra={
                "session_id": session.id,
                "customer_id": customer_id,
            },
        )
        return CheckoutSessionResponse(
            checkout_url=session.url or "",
            session_id=session.id,
        )
    except stripe.StripeError as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise


async def create_portal_session(
    customer_id: str,
    return_url: str | None = None,
) -> PortalSessionResponse:
    """
    Create a Stripe Customer Portal session for managing subscriptions.

    Args:
        customer_id: Stripe customer ID (cus_...)
        return_url: URL to return to after leaving portal

    Returns:
        PortalSessionResponse with portal URL
    """
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url or settings.FRONTEND_URL,
        )
        logger.info(
            "Created portal session",
            extra={
                "session_id": session.id,
                "customer_id": customer_id,
            },
        )
        return PortalSessionResponse(portal_url=session.url)
    except stripe.StripeError as e:
        logger.error(f"Failed to create portal session: {e}")
        raise


def verify_webhook_signature(payload: bytes, signature: str) -> stripe.Event:
    """
    Verify the Stripe webhook signature and construct the event.

    Args:
        payload: Raw request body
        signature: Stripe-Signature header value

    Returns:
        Verified Stripe event

    Raises:
        ValueError: If signature verification fails
    """
    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )
        return event
    except stripe.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise ValueError("Invalid webhook signature") from None


async def handle_webhook_event(event: stripe.Event) -> WebhookResult:
    """
    Handle a verified Stripe webhook event.

    Processes events and returns the result for database updates.

    Args:
        event: Verified Stripe event object

    Returns:
        WebhookResult with processing outcome
    """
    event_type = event.type
    data_object = event.data.object

    logger.info(f"Processing webhook event: {event_type}")

    # Handle subscription-related events
    if event_type == "checkout.session.completed":
        return await _handle_checkout_completed(data_object)

    elif event_type == "invoice.payment_succeeded":
        return await _handle_payment_succeeded(data_object)

    elif event_type == "invoice.payment_failed":
        return await _handle_payment_failed(data_object)

    elif event_type == "customer.subscription.updated":
        return await _handle_subscription_updated(data_object)

    elif event_type == "customer.subscription.deleted":
        return await _handle_subscription_deleted(data_object)

    else:
        logger.info(f"Unhandled webhook event type: {event_type}")
        return WebhookResult(
            success=True,
            event_type=event_type,
            message=f"Event type {event_type} not handled",
        )


async def _handle_checkout_completed(session: Any) -> WebhookResult:
    """Handle checkout.session.completed event."""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")

    logger.info(
        "Checkout completed",
        extra={
            "customer_id": customer_id,
            "subscription_id": subscription_id,
        },
    )

    # The subscription is now active
    return WebhookResult(
        success=True,
        event_type="checkout.session.completed",
        customer_id=customer_id,
        subscription_status="ACTIVE",
        message="Subscription activated via checkout",
    )


async def _handle_payment_succeeded(invoice: Any) -> WebhookResult:
    """Handle invoice.payment_succeeded event."""
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")

    logger.info(
        "Payment succeeded",
        extra={
            "customer_id": customer_id,
            "subscription_id": subscription_id,
            "amount_paid": invoice.get("amount_paid"),
        },
    )

    return WebhookResult(
        success=True,
        event_type="invoice.payment_succeeded",
        customer_id=customer_id,
        subscription_status="ACTIVE",
        message="Payment successful",
    )


async def _handle_payment_failed(invoice: Any) -> WebhookResult:
    """Handle invoice.payment_failed event."""
    customer_id = invoice.get("customer")

    logger.warning(
        "Payment failed",
        extra={
            "customer_id": customer_id,
            "attempt_count": invoice.get("attempt_count"),
        },
    )

    return WebhookResult(
        success=True,
        event_type="invoice.payment_failed",
        customer_id=customer_id,
        subscription_status="PAST_DUE",
        message="Payment failed",
    )


async def _handle_subscription_updated(subscription: Any) -> WebhookResult:
    """Handle customer.subscription.updated event."""
    customer_id = subscription.get("customer")
    status = subscription.get("status")

    # Map Stripe status to our status
    status_map = {
        "active": "ACTIVE",
        "past_due": "PAST_DUE",
        "canceled": "CANCELED",
        "unpaid": "PAST_DUE",
        "incomplete": "PENDING",
        "incomplete_expired": "CANCELED",
        "trialing": "TRIALING",
        "paused": "PAUSED",
    }
    mapped_status = status_map.get(status, "UNKNOWN")

    logger.info(
        "Subscription updated",
        extra={
            "customer_id": customer_id,
            "stripe_status": status,
            "mapped_status": mapped_status,
        },
    )

    return WebhookResult(
        success=True,
        event_type="customer.subscription.updated",
        customer_id=customer_id,
        subscription_status=mapped_status,
        message=f"Subscription status: {status}",
    )


async def _handle_subscription_deleted(subscription: Any) -> WebhookResult:
    """Handle customer.subscription.deleted event."""
    customer_id = subscription.get("customer")

    logger.info(
        "Subscription deleted",
        extra={
            "customer_id": customer_id,
        },
    )

    return WebhookResult(
        success=True,
        event_type="customer.subscription.deleted",
        customer_id=customer_id,
        subscription_status="CANCELED",
        message="Subscription canceled",
    )


async def get_customer_subscriptions(customer_id: str) -> list[dict[str, Any]]:
    """
    Get active subscriptions for a customer.

    Args:
        customer_id: Stripe customer ID

    Returns:
        List of subscription details
    """
    try:
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="all",
            limit=10,
        )
        return [
            {
                "id": sub.id,
                "status": sub.status,
                "current_period_end": sub.current_period_end,
                "cancel_at_period_end": sub.cancel_at_period_end,
                "plan_id": sub.items.data[0].price.id if sub.items.data else None,
            }
            for sub in subscriptions.data
        ]
    except stripe.StripeError as e:
        logger.error(f"Failed to get subscriptions: {e}")
        raise
