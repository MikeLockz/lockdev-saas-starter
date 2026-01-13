"""
Stripe Billing Service

This module handles Stripe subscription management for Organizations and Patients.
Epic 22 - Complete Billing & Subscription Management
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

import stripe
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.billing import BillingTransaction, SubscriptionOverride
from src.models.organizations import Organization
from src.models.profiles import Patient
from src.services.email import email_service
from src.services.receipt import receipt_generator

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
    except Exception as e:
        logger.error(f"Webhook signature checking failed with unexpected error: {e}")
        raise ValueError("Invalid webhook signature") from None


async def _get_owner_from_customer(
    customer_id: str,
    db: AsyncSession,
) -> tuple[UUID, str] | tuple[None, None]:
    """Get owner ID and type from Stripe customer ID."""
    # Check Organization
    result = await db.execute(select(Organization).where(Organization.stripe_customer_id == customer_id))
    org = result.scalar_one_or_none()
    if org:
        return org.id, "ORGANIZATION"

    # Check Patient
    result = await db.execute(select(Patient).where(Patient.stripe_customer_id == customer_id))
    patient = result.scalar_one_or_none()
    if patient:
        return patient.id, "PATIENT"

    return None, None


async def handle_webhook_event(event: stripe.Event, db: AsyncSession) -> WebhookResult:
    """
    Handle a verified Stripe webhook event.

    Processes events and returns the result for database updates.

    Args:
        event: Verified Stripe event object
        db: Database session

    Returns:
        WebhookResult with processing outcome
    """
    event_type = event.type
    data_object = event.data.object

    logger.info(f"Processing webhook event: {event_type}")

    # Handle subscription-related events
    if event_type == "checkout.session.completed":
        return await _handle_checkout_completed(data_object, db)

    elif event_type == "invoice.payment_succeeded":
        return await _handle_payment_succeeded(data_object, db)

    elif event_type == "invoice.payment_failed":
        return await _handle_payment_failed(data_object, db)

    elif event_type == "customer.subscription.updated":
        return await _handle_subscription_updated(data_object, db)

    elif event_type == "customer.subscription.deleted":
        return await _handle_subscription_deleted(data_object, db)

    else:
        logger.info(f"Unhandled webhook event type: {event_type}")
        return WebhookResult(
            success=True,
            event_type=event_type,
            message=f"Event type {event_type} not handled",
        )


async def _handle_checkout_completed(session: Any, db: AsyncSession) -> WebhookResult:
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


async def _handle_payment_succeeded(invoice: Any, db: AsyncSession) -> WebhookResult:
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

    # Record transaction
    transaction = None
    if customer_id:
        owner_id, owner_type = await _get_owner_from_customer(customer_id, db)
        if owner_id:
            description = None
            if invoice.get("lines") and invoice["lines"].get("data"):
                description = invoice["lines"]["data"][0].get("description")

            transaction = await record_transaction(
                db=db,
                owner_id=owner_id,
                owner_type=owner_type,
                stripe_payment_intent_id=invoice.get("payment_intent"),
                stripe_invoice_id=invoice.get("id"),
                stripe_charge_id=invoice.get("charge"),
                amount_cents=invoice.get("amount_paid", 0),
                currency=invoice.get("currency", "usd"),
                status="SUCCEEDED",
                description=f"Subscription payment - {description}" if description else "Subscription payment",
                receipt_url=invoice.get("hosted_invoice_url"),
                receipt_number=invoice.get("number"),
            )

            # Send receipt email (Epic 22)
            if owner_type == "PATIENT":
                patient = await db.get(Patient, owner_id)
                if patient:
                    plan_name = description or "Subscription"
                    start_date = datetime.fromtimestamp(invoice.get("period_start", datetime.now().timestamp()))
                    end_date = datetime.fromtimestamp(invoice.get("period_end", datetime.now().timestamp()))
                    billing_period = f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}"

                    payment_method = "Credit Card"
                    if invoice.get("payment_method_details") and invoice["payment_method_details"].get("card"):
                        payment_method = f"Card ending in {invoice['payment_method_details']['card']['last4']}"

                    # Generate PDF
                    try:
                        pdf_bytes = receipt_generator.generate_pdf_receipt(
                            transaction=transaction,
                            patient=patient,
                            plan_name=plan_name,
                            billing_period=billing_period,
                            payment_method=payment_method,
                        )

                        # Save receipt
                        receipt_url = await receipt_generator.save_receipt_to_storage(pdf_bytes, str(transaction.id))

                        # Send Email
                        await email_service.send_payment_success_email(
                            db=db,
                            patient=patient,
                            amount_cents=transaction.amount_cents,
                            receipt_number=transaction.receipt_number or str(transaction.id),
                            payment_date=transaction.created_at,
                            payment_method=payment_method,
                            plan_name=plan_name,
                            billing_period=billing_period,
                            receipt_url=receipt_url,
                            pdf_attachment=pdf_bytes,
                        )
                    except Exception as e:
                        logger.error(f"Failed to generate/send receipt: {e}")

    return WebhookResult(
        success=True,
        event_type="invoice.payment_succeeded",
        customer_id=customer_id,
        subscription_status="ACTIVE",
        message="Payment successful",
    )


async def _handle_payment_failed(invoice: Any, db: AsyncSession) -> WebhookResult:
    """Handle invoice.payment_failed event."""
    customer_id = invoice.get("customer")

    logger.warning(
        "Payment failed",
        extra={
            "customer_id": customer_id,
            "attempt_count": invoice.get("attempt_count"),
        },
    )

    # Record transaction failure
    if customer_id:
        owner_id, owner_type = await _get_owner_from_customer(customer_id, db)
        if owner_id:
            description = None
            if invoice.get("lines") and invoice["lines"].get("data"):
                description = invoice["lines"]["data"][0].get("description")

            await record_transaction(
                db=db,
                owner_id=owner_id,
                owner_type=owner_type,
                stripe_payment_intent_id=invoice.get("payment_intent"),
                stripe_invoice_id=invoice.get("id"),
                stripe_charge_id=invoice.get("charge"),
                amount_cents=invoice.get("amount_due", 0),
                currency=invoice.get("currency", "usd"),
                status="FAILED",
                description=f"Payment failed - {description}" if description else "Payment failed",
                receipt_url=invoice.get("hosted_invoice_url"),
                receipt_number=invoice.get("number"),
            )

            # Send failure email
            if owner_type == "PATIENT":
                patient = await db.get(Patient, owner_id)
                if patient:
                    try:
                        await email_service.send_payment_failed_email(
                            db=db,
                            patient=patient,
                            amount_cents=invoice.get("amount_due", 0),
                            failure_reason=invoice.get("last_finalization_error", {}).get("message", "Unknown"),
                            attempt_count=invoice.get("attempt_count", 1),
                            update_payment_url=f"{settings.FRONTEND_URL}/patient/billing",
                        )
                    except Exception as e:
                        logger.error(f"Failed to send failure email: {e}")

    return WebhookResult(
        success=True,
        event_type="invoice.payment_failed",
        customer_id=customer_id,
        subscription_status="PAST_DUE",
        message="Payment failed",
    )


async def _handle_subscription_updated(subscription: Any, db: AsyncSession) -> WebhookResult:
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


async def _handle_subscription_deleted(subscription: Any, db: AsyncSession) -> WebhookResult:
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


# ============================================================================
# PATIENT BILLING FUNCTIONS (Epic 22)
# ============================================================================


async def get_or_create_patient_customer(
    db: AsyncSession,
    patient_id: UUID,
) -> str:
    """
    Get or create Stripe customer for a patient.

    Args:
        db: Database session
        patient_id: Patient UUID

    Returns:
        Stripe customer ID (cus_...)

    Raises:
        ValueError: If patient not found
    """
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise ValueError(f"Patient {patient_id} not found")

    # Return existing customer if available
    if patient.stripe_customer_id:
        logger.info(f"Using existing Stripe customer {patient.stripe_customer_id} for patient {patient_id}")
        return patient.stripe_customer_id

    # Get patient email from user account
    patient_email = None
    patient_name = f"{patient.first_name} {patient.last_name}"

    if patient.user_id:
        from src.models.users import User

        user = await db.get(User, patient.user_id)
        if user:
            patient_email = user.email

    if not patient_email:
        # Try to get email from contact methods
        from src.models.contacts import ContactMethod

        result = await db.execute(
            select(ContactMethod)
            .where(
                ContactMethod.patient_id == patient_id,
                ContactMethod.contact_type == "EMAIL",
                ContactMethod.is_primary,
            )
            .limit(1)
        )
        contact = result.scalar_one_or_none()
        if contact:
            patient_email = contact.contact_value

    if not patient_email:
        raise ValueError(f"Patient {patient_id} has no email address")

    # Create new Stripe customer
    customer_id = await create_customer(
        owner_id=str(patient_id),
        owner_type=CustomerType.PATIENT,
        email=patient_email,
        name=patient_name,
    )

    # Save to database
    patient.stripe_customer_id = customer_id
    await db.commit()
    await db.refresh(patient)

    logger.info(f"Created Stripe customer {customer_id} for patient {patient_id}")
    return customer_id


async def cancel_subscription(
    customer_id: str,
    cancel_immediately: bool = False,
) -> dict[str, Any]:
    """
    Cancel a Stripe subscription.

    Args:
        customer_id: Stripe customer ID
        cancel_immediately: If True, cancel now; if False, cancel at period end

    Returns:
        Dict with cancellation details

    Raises:
        ValueError: If no active subscription found
    """
    try:
        # Get active subscriptions
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            limit=1,
        )

        if not subscriptions.data:
            raise ValueError("No active subscription found")

        subscription = subscriptions.data[0]

        # Cancel immediately or at period end
        if cancel_immediately:
            cancelled = stripe.Subscription.cancel(subscription.id)
            logger.info(f"Immediately cancelled subscription {subscription.id} for customer {customer_id}")
        else:
            cancelled = stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=True,
            )
            logger.info(f"Scheduled cancellation at period end for subscription {subscription.id}")

        return {
            "subscription_id": cancelled.id,
            "status": cancelled.status,
            "cancelled_at": cancelled.canceled_at,
            "cancel_at_period_end": cancelled.cancel_at_period_end,
        }
    except stripe.StripeError as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise


async def record_transaction(
    db: AsyncSession,
    owner_id: UUID,
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
    managed_by_proxy_id: UUID | None = None,
    metadata: dict | None = None,
) -> BillingTransaction:
    """
    Record a billing transaction in the database.

    Args:
        db: Database session
        owner_id: Patient or Organization ID
        owner_type: "PATIENT" or "ORGANIZATION"
        stripe_payment_intent_id: Stripe payment intent ID
        stripe_invoice_id: Stripe invoice ID
        stripe_charge_id: Stripe charge ID
        amount_cents: Amount in cents
        currency: Currency code (e.g., "usd")
        status: Transaction status
        description: Transaction description
        receipt_url: URL to receipt
        receipt_number: Receipt number
        managed_by_proxy_id: Proxy user ID if transaction was initiated by proxy
        metadata: Additional metadata

    Returns:
        Created BillingTransaction object
    """
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
        managed_by_proxy_id=managed_by_proxy_id,
        meta_data=metadata or {},
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    logger.info(
        f"Recorded transaction {transaction.id}: {status} ${amount_cents / 100:.2f} for {owner_type} {owner_id}"
    )

    return transaction


async def get_subscription_status(customer_id: str) -> dict[str, Any]:
    """
    Get current subscription status for a customer.

    Args:
        customer_id: Stripe customer ID

    Returns:
        Dict with subscription status details
    """
    try:
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            limit=1,
        )

        if not subscriptions.data:
            return {
                "status": "NONE",
                "plan_id": None,
                "current_period_end": None,
                "cancel_at_period_end": False,
            }

        sub = subscriptions.data[0]

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

        return {
            "status": status_map.get(sub.status, "UNKNOWN"),
            "plan_id": sub.items.data[0].price.id if sub.items.data else None,
            "current_period_end": sub.current_period_end,
            "cancel_at_period_end": sub.cancel_at_period_end,
        }
    except stripe.StripeError as e:
        logger.error(f"Failed to get subscription status: {e}")
        raise


async def refund_transaction(
    db: AsyncSession,
    transaction_id: UUID,
    amount_cents: int | None,
    reason: str,
    refunded_by: UUID,
) -> dict[str, Any]:
    """
    Refund a transaction (full or partial).

    Args:
        db: Database session
        transaction_id: Transaction UUID
        amount_cents: Amount to refund (None for full refund)
        reason: Refund reason
        refunded_by: User ID issuing the refund

    Returns:
        Dict with refund details

    Raises:
        ValueError: If transaction not found or already refunded
    """
    transaction = await db.get(BillingTransaction, transaction_id)
    if not transaction:
        raise ValueError("Transaction not found")

    if transaction.status == "REFUNDED":
        raise ValueError("Transaction already refunded")

    if not transaction.stripe_payment_intent_id:
        raise ValueError("No Stripe payment intent ID")

    # Determine refund amount
    refund_amount = amount_cents if amount_cents else transaction.amount_cents

    try:
        # Issue refund via Stripe
        refund = stripe.Refund.create(
            payment_intent=transaction.stripe_payment_intent_id,
            amount=refund_amount,
            reason="requested_by_customer",
            metadata={"reason": reason},
        )

        # Update transaction
        transaction.status = "REFUNDED"
        transaction.refunded_at = datetime.utcnow()
        transaction.refunded_by = refunded_by
        transaction.refund_reason = reason

        await db.commit()

        logger.info(f"Refunded transaction {transaction_id}: ${refund_amount / 100:.2f} (reason: {reason})")

        return {
            "refund_id": refund.id,
            "amount_refunded": refund_amount,
        }
    except stripe.StripeError as e:
        logger.error(f"Failed to process refund: {e}")
        raise


async def grant_free_subscription(
    db: AsyncSession,
    owner_id: UUID,
    owner_type: str,
    reason: str,
    granted_by: UUID,
    duration_months: int | None = None,
) -> SubscriptionOverride:
    """
    Grant a free subscription to a patient or organization.

    Args:
        db: Database session
        owner_id: Patient or Organization ID
        owner_type: "PATIENT" or "ORGANIZATION"
        reason: Reason for granting free subscription
        granted_by: User ID granting the subscription
        duration_months: Duration in months (None for indefinite)

    Returns:
        Created SubscriptionOverride object
    """
    # Calculate expiration date
    expires_at = None
    if duration_months:
        from datetime import timedelta

        expires_at = datetime.utcnow() + timedelta(days=duration_months * 30)

    # Create override
    override = SubscriptionOverride(
        owner_id=owner_id,
        owner_type=owner_type,
        override_type="FREE",
        granted_by=granted_by,
        reason=reason,
        expires_at=expires_at,
    )

    db.add(override)

    # If they have an active Stripe subscription, cancel it
    if owner_type == "PATIENT":
        patient = await db.get(Patient, owner_id)
        if patient and patient.stripe_customer_id:
            try:
                await cancel_subscription(patient.stripe_customer_id, cancel_immediately=True)
                logger.info(f"Cancelled Stripe subscription for patient {owner_id} (free override granted)")
            except Exception as e:
                logger.warning(f"Could not cancel Stripe subscription: {e}")

    await db.commit()
    await db.refresh(override)

    logger.info(f"Granted free subscription to {owner_type} {owner_id} for {duration_months or 'unlimited'} months")

    return override


# ============================================================================
# ADMIN BILLING FUNCTIONS (Story 22.4)
# ============================================================================


async def get_all_subscriptions(
    db: AsyncSession,
    status: str | None = None,
    owner_type: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[dict[str, Any]], int]:
    """
    Get all subscriptions across organizations and patients.

    Args:
        db: Database session
        status: Filter by subscription status
        owner_type: Filter by PATIENT or ORGANIZATION
        search: Search by name or email
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Tuple of (subscriptions list, total count)
    """
    from src.models.users import User

    subscriptions = []

    # Get patient subscriptions
    if owner_type is None or owner_type == "PATIENT":
        patient_query = select(Patient).where(Patient.stripe_customer_id.isnot(None))

        if status:
            patient_query = patient_query.where(Patient.subscription_status == status)

        if search:
            patient_query = patient_query.where(
                (Patient.first_name.ilike(f"%{search}%"))
                | (Patient.last_name.ilike(f"%{search}%"))
            )

        result = await db.execute(patient_query)
        patients = result.scalars().all()

        for patient in patients:
            # Get billing manager name if assigned
            billing_manager_name = None
            if patient.billing_manager_id:
                manager = await db.get(User, patient.billing_manager_id)
                if manager:
                    billing_manager_name = manager.display_name or manager.email

            # Get patient email from user
            patient_email = None
            if patient.user_id:
                user = await db.get(User, patient.user_id)
                if user:
                    patient_email = user.email

            subscriptions.append({
                "owner_id": patient.id,
                "owner_type": "PATIENT",
                "owner_name": f"{patient.first_name} {patient.last_name}",
                "owner_email": patient_email,
                "stripe_customer_id": patient.stripe_customer_id,
                "subscription_status": patient.subscription_status,
                "plan_id": None,
                "current_period_end": None,
                "mrr_cents": 0,
                "created_at": patient.created_at,
                "cancelled_at": None,
                "billing_manager_id": patient.billing_manager_id,
                "billing_manager_name": billing_manager_name,
            })

    # Get organization subscriptions
    if owner_type is None or owner_type == "ORGANIZATION":
        org_query = select(Organization).where(Organization.stripe_customer_id.isnot(None))

        if status:
            org_query = org_query.where(Organization.subscription_status == status)

        if search:
            org_query = org_query.where(Organization.name.ilike(f"%{search}%"))

        result = await db.execute(org_query)
        orgs = result.scalars().all()

        for org in orgs:
            subscriptions.append({
                "owner_id": org.id,
                "owner_type": "ORGANIZATION",
                "owner_name": org.name,
                "owner_email": None,
                "stripe_customer_id": org.stripe_customer_id,
                "subscription_status": org.subscription_status,
                "plan_id": None,
                "current_period_end": None,
                "mrr_cents": 0,
                "created_at": org.created_at,
                "cancelled_at": None,
                "billing_manager_id": None,
                "billing_manager_name": None,
            })

    # Sort by created_at desc
    subscriptions.sort(key=lambda x: x["created_at"] or datetime.min, reverse=True)

    # Get total count
    total = len(subscriptions)

    # Paginate
    offset = (page - 1) * page_size
    subscriptions = subscriptions[offset : offset + page_size]

    return subscriptions, total


async def calculate_billing_analytics(db: AsyncSession) -> dict[str, Any]:
    """
    Calculate billing analytics.

    Args:
        db: Database session

    Returns:
        Dict with billing analytics metrics
    """
    from datetime import timedelta

    from sqlalchemy import func

    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Count active patient subscriptions
    patient_active_count = await db.scalar(
        select(func.count())
        .select_from(Patient)
        .where(Patient.subscription_status.in_(["ACTIVE", "TRIALING"]))
    ) or 0

    # Count active org subscriptions
    org_active_count = await db.scalar(
        select(func.count())
        .select_from(Organization)
        .where(Organization.subscription_status.in_(["ACTIVE", "TRIALING"]))
    ) or 0

    total_active = patient_active_count + org_active_count

    # Count new subscriptions this month (patients that became ACTIVE this month)
    # This is approximate - ideally track subscription_activated_at
    new_this_month = await db.scalar(
        select(func.count())
        .select_from(BillingTransaction)
        .where(
            BillingTransaction.status == "SUCCEEDED",
            BillingTransaction.created_at >= month_start,
            BillingTransaction.description.ilike("%subscription%"),
        )
    ) or 0

    # Count failed payments this month
    failed_this_month = await db.scalar(
        select(func.count())
        .select_from(BillingTransaction)
        .where(
            BillingTransaction.status == "FAILED",
            BillingTransaction.created_at >= month_start,
        )
    ) or 0

    # Total revenue this month
    revenue_this_month = await db.scalar(
        select(func.sum(BillingTransaction.amount_cents))
        .where(
            BillingTransaction.status == "SUCCEEDED",
            BillingTransaction.created_at >= month_start,
        )
    ) or 0

    # Cancelled subscriptions this month (count refunds as proxy)
    cancelled_this_month = await db.scalar(
        select(func.count())
        .select_from(BillingTransaction)
        .where(
            BillingTransaction.status == "REFUNDED",
            BillingTransaction.refunded_at >= month_start,
        )
    ) or 0

    # Calculate churn rate
    churn_rate = 0.0
    if total_active > 0:
        churn_rate = cancelled_this_month / total_active

    # Calculate ARPU
    arpu = 0
    if total_active > 0:
        arpu = int(revenue_this_month / total_active)

    return {
        "total_active_subscriptions": total_active,
        "total_mrr_cents": 0,  # Would need Stripe API call for accurate MRR
        "new_subscriptions_this_month": new_this_month,
        "cancelled_subscriptions_this_month": cancelled_this_month,
        "churn_rate": churn_rate,
        "average_revenue_per_user_cents": arpu,
        "failed_payments_this_month": failed_this_month,
        "total_revenue_this_month_cents": revenue_this_month,
    }

