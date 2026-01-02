"""
Webhooks API

This module handles incoming webhooks from external services.
"""

import logging

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import update

from src.database import AsyncSessionLocal
from src.models.organizations import Organization
from src.models.profiles import Patient
from src.services.billing import (
    WebhookResult,
    handle_webhook_event,
    verify_webhook_signature,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/stripe")
async def handle_stripe_webhook(request: Request) -> dict:
    """
    Handle incoming Stripe webhook events.

    This endpoint receives events from Stripe and processes them:
    - Verifies the webhook signature for security
    - Parses the event and dispatches to appropriate handlers
    - Updates database records based on event type

    **Security:**
    - Signature verification using STRIPE_WEBHOOK_SECRET
    - Raw body parsing to prevent tampering

    **Handled Events:**
    - checkout.session.completed: Subscription activated
    - invoice.payment_succeeded: Payment confirmed
    - invoice.payment_failed: Payment failed, status updated
    - customer.subscription.updated: Subscription status changed
    - customer.subscription.deleted: Subscription canceled

    Returns:
        Success response for Stripe acknowledgment
    """
    # Get raw body for signature verification
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature")

    if not signature:
        logger.warning("Missing Stripe-Signature header")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header",
        )

    # Verify signature and construct event
    try:
        event = verify_webhook_signature(payload, signature)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        ) from None

    # Process the event
    result = await handle_webhook_event(event)

    # Update database based on result
    if result.customer_id and result.subscription_status:
        await _update_subscription_status(result)

    return {"received": True, "event_type": event.type}


async def _update_subscription_status(result: WebhookResult) -> None:
    """
    Update the subscription status in the database.

    Looks up the customer in both organizations and patients tables
    and updates the subscription_status field.

    Args:
        result: WebhookResult with customer_id and subscription_status
    """
    async with AsyncSessionLocal() as db:
        # Try to update organization first
        org_result = await db.execute(
            update(Organization)
            .where(Organization.stripe_customer_id == result.customer_id)
            .values(subscription_status=result.subscription_status)
            .returning(Organization.id)
        )
        org_updated = org_result.fetchone()

        if org_updated:
            logger.info(
                "Updated organization subscription status",
                extra={
                    "organization_id": str(org_updated[0]),
                    "subscription_status": result.subscription_status,
                },
            )
            await db.commit()
            return

        # Try patient if organization not found
        patient_result = await db.execute(
            update(Patient)
            .where(Patient.stripe_customer_id == result.customer_id)
            .values(subscription_status=result.subscription_status)
            .returning(Patient.id)
        )
        patient_updated = patient_result.fetchone()

        if patient_updated:
            logger.info(
                "Updated patient subscription status",
                extra={
                    "patient_id": str(patient_updated[0]),
                    "subscription_status": result.subscription_status,
                },
            )
            await db.commit()
            return

        logger.warning(
            "Customer not found for subscription update",
            extra={
                "customer_id": result.customer_id,
                "subscription_status": result.subscription_status,
            },
        )
