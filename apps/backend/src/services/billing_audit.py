"""
Billing Audit Service

Service for auditing billing operations with comprehensive logging.
Story 22.6 - Epic 22: Complete Billing & Subscription Management
"""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit import AuditLog

logger = logging.getLogger(__name__)


# =============================================================================
# Billing Audit Event Types
# =============================================================================


class BillingAuditEventType:
    """Billing-specific audit event types."""

    # Checkout & Subscription Events
    CHECKOUT_CREATED = "billing.checkout.created"
    SUBSCRIPTION_CREATED = "billing.subscription.created"
    SUBSCRIPTION_UPDATED = "billing.subscription.updated"
    SUBSCRIPTION_CANCELLED = "billing.subscription.cancelled"

    # Payment Events
    PAYMENT_SUCCEEDED = "billing.payment.succeeded"
    PAYMENT_FAILED = "billing.payment.failed"

    # Admin Actions
    REFUND_ISSUED = "billing.refund.issued"
    FREE_SUBSCRIPTION_GRANTED = "billing.free_subscription.granted"
    OVERRIDE_CREATED = "billing.override.created"
    OVERRIDE_REVOKED = "billing.override.revoked"

    # Portal & Webhook Events
    PORTAL_ACCESSED = "billing.portal.accessed"
    WEBHOOK_RECEIVED = "billing.webhook.received"
    WEBHOOK_FAILED = "billing.webhook.failed"

    # Proxy Billing Events
    BILLING_MANAGER_ASSIGNED = "billing.manager.assigned"
    BILLING_MANAGER_REMOVED = "billing.manager.removed"
    PROXY_CHECKOUT_CREATED = "billing.proxy.checkout.created"
    PROXY_SUBSCRIPTION_CANCELLED = "billing.proxy.subscription.cancelled"


# =============================================================================
# Billing Audit Service
# =============================================================================


class BillingAuditService:
    """Service for auditing billing operations."""

    @staticmethod
    async def log_checkout_created(
        db: AsyncSession,
        user_id: UUID,
        owner_id: UUID,
        owner_type: str,
        price_id: str,
        session_id: str,
        metadata: dict | None = None,
    ) -> None:
        """Log checkout session creation."""
        audit = AuditLog(
            actor_user_id=user_id,
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action_type="CREATE",
            changes_json={
                "event_type": BillingAuditEventType.CHECKOUT_CREATED,
                "price_id": price_id,
                "session_id": session_id,
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Checkout created: user=%s, owner=%s, owner_type=%s, price=%s",
            user_id,
            owner_id,
            owner_type,
            price_id,
        )

    @staticmethod
    async def log_payment_succeeded(
        db: AsyncSession,
        owner_id: UUID,
        owner_type: str,
        amount_cents: int,
        currency: str,
        transaction_id: UUID,
        stripe_invoice_id: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Log successful payment."""
        audit = AuditLog(
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action_type="CREATE",
            changes_json={
                "event_type": BillingAuditEventType.PAYMENT_SUCCEEDED,
                "amount_cents": amount_cents,
                "currency": currency,
                "transaction_id": str(transaction_id),
                "stripe_invoice_id": stripe_invoice_id,
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Payment succeeded: owner=%s, amount=%d, currency=%s, invoice=%s",
            owner_id,
            amount_cents,
            currency,
            stripe_invoice_id,
        )

    @staticmethod
    async def log_payment_failed(
        db: AsyncSession,
        owner_id: UUID,
        owner_type: str,
        amount_cents: int,
        currency: str,
        reason: str,
        attempt_count: int,
        metadata: dict | None = None,
    ) -> None:
        """Log failed payment."""
        audit = AuditLog(
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action_type="UPDATE",
            changes_json={
                "event_type": BillingAuditEventType.PAYMENT_FAILED,
                "amount_cents": amount_cents,
                "currency": currency,
                "reason": reason,
                "attempt_count": attempt_count,
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.warning(
            "Payment failed: owner=%s, amount=%d, reason=%s, attempt=%d",
            owner_id,
            amount_cents,
            reason,
            attempt_count,
        )

    @staticmethod
    async def log_refund_issued(
        db: AsyncSession,
        user_id: UUID,
        transaction_id: UUID,
        amount_cents: int,
        reason: str,
        refund_id: str,
        metadata: dict | None = None,
    ) -> None:
        """Log refund issuance."""
        audit = AuditLog(
            actor_user_id=user_id,
            resource_type="transaction",
            resource_id=transaction_id,
            action_type="UPDATE",
            changes_json={
                "event_type": BillingAuditEventType.REFUND_ISSUED,
                "amount_cents": amount_cents,
                "reason": reason,
                "refund_id": refund_id,
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.warning(
            "Refund issued: admin=%s, transaction=%s, amount=%d, reason=%s",
            user_id,
            transaction_id,
            amount_cents,
            reason,
        )

    @staticmethod
    async def log_free_subscription_granted(
        db: AsyncSession,
        user_id: UUID,
        owner_id: UUID,
        owner_type: str,
        reason: str,
        duration_months: int | None,
        override_id: UUID,
        metadata: dict | None = None,
    ) -> None:
        """Log free subscription grant."""
        audit = AuditLog(
            actor_user_id=user_id,
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action_type="CREATE",
            changes_json={
                "event_type": BillingAuditEventType.FREE_SUBSCRIPTION_GRANTED,
                "reason": reason,
                "duration_months": duration_months,
                "override_id": str(override_id),
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Free subscription granted: admin=%s, owner=%s, duration=%s, reason=%s",
            user_id,
            owner_id,
            duration_months,
            reason,
        )

    @staticmethod
    async def log_subscription_cancelled(
        db: AsyncSession,
        user_id: UUID | None,
        owner_id: UUID,
        owner_type: str,
        reason: str | None,
        cancelled_immediately: bool,
        metadata: dict | None = None,
    ) -> None:
        """Log subscription cancellation."""
        audit = AuditLog(
            actor_user_id=user_id,
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action_type="UPDATE",
            changes_json={
                "event_type": BillingAuditEventType.SUBSCRIPTION_CANCELLED,
                "reason": reason,
                "cancelled_immediately": cancelled_immediately,
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Subscription cancelled: user=%s, owner=%s, immediate=%s, reason=%s",
            user_id,
            owner_id,
            cancelled_immediately,
            reason,
        )

    @staticmethod
    async def log_webhook_received(
        db: AsyncSession,
        event_type: str,
        event_id: str,
        customer_id: str | None,
        processed_successfully: bool,
        error: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Log webhook receipt."""
        audit_event_type = (
            BillingAuditEventType.WEBHOOK_RECEIVED if processed_successfully else BillingAuditEventType.WEBHOOK_FAILED
        )
        audit = AuditLog(
            resource_type="webhook",
            resource_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            action_type="CREATE",
            changes_json={
                "event_type": audit_event_type,
                "stripe_event_type": event_type,
                "stripe_event_id": event_id,
                "customer_id": customer_id,
                "error": error,
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        if processed_successfully:
            logger.info("Webhook processed: type=%s, id=%s", event_type, event_id)
        else:
            logger.error("Webhook failed: type=%s, id=%s, error=%s", event_type, event_id, error)

    # =========================================================================
    # Proxy Billing Audit Methods
    # =========================================================================

    @staticmethod
    async def log_billing_manager_assigned(
        db: AsyncSession,
        patient_id: UUID,
        proxy_user_id: UUID,
        assigned_by: UUID,
        metadata: dict | None = None,
    ) -> None:
        """Log billing manager assignment."""
        audit = AuditLog(
            actor_user_id=assigned_by,
            resource_type="patient",
            resource_id=patient_id,
            action_type="UPDATE",
            changes_json={
                "event_type": BillingAuditEventType.BILLING_MANAGER_ASSIGNED,
                "proxy_user_id": str(proxy_user_id),
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Billing manager assigned: patient=%s, proxy=%s, assigned_by=%s",
            patient_id,
            proxy_user_id,
            assigned_by,
        )

    @staticmethod
    async def log_billing_manager_removed(
        db: AsyncSession,
        patient_id: UUID,
        proxy_user_id: UUID,
        removed_by: UUID,
        metadata: dict | None = None,
    ) -> None:
        """Log billing manager removal."""
        audit = AuditLog(
            actor_user_id=removed_by,
            resource_type="patient",
            resource_id=patient_id,
            action_type="UPDATE",
            changes_json={
                "event_type": BillingAuditEventType.BILLING_MANAGER_REMOVED,
                "proxy_user_id": str(proxy_user_id),
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Billing manager removed: patient=%s, proxy=%s, removed_by=%s",
            patient_id,
            proxy_user_id,
            removed_by,
        )

    @staticmethod
    async def log_proxy_checkout_created(
        db: AsyncSession,
        proxy_user_id: UUID,
        patient_id: UUID,
        price_id: str,
        session_id: str,
        metadata: dict | None = None,
    ) -> None:
        """Log proxy-initiated checkout."""
        audit = AuditLog(
            actor_user_id=proxy_user_id,
            resource_type="patient",
            resource_id=patient_id,
            action_type="CREATE",
            changes_json={
                "event_type": BillingAuditEventType.PROXY_CHECKOUT_CREATED,
                "price_id": price_id,
                "session_id": session_id,
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Proxy checkout created: proxy=%s, patient=%s, price=%s",
            proxy_user_id,
            patient_id,
            price_id,
        )

    @staticmethod
    async def log_proxy_subscription_cancelled(
        db: AsyncSession,
        proxy_user_id: UUID,
        patient_id: UUID,
        reason: str | None,
        metadata: dict | None = None,
    ) -> None:
        """Log proxy-initiated subscription cancellation."""
        audit = AuditLog(
            actor_user_id=proxy_user_id,
            resource_type="patient",
            resource_id=patient_id,
            action_type="UPDATE",
            changes_json={
                "event_type": BillingAuditEventType.PROXY_SUBSCRIPTION_CANCELLED,
                "reason": reason,
                **(metadata or {}),
            },
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Proxy cancelled subscription: proxy=%s, patient=%s, reason=%s",
            proxy_user_id,
            patient_id,
            reason,
        )


# Singleton instance for convenience
billing_audit = BillingAuditService()
