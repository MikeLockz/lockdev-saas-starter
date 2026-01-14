"""
Billing Metrics Service

Service for tracking billing metrics using structured logging.
Story 22.6 - Epic 22: Complete Billing & Subscription Management
"""

import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Billing Metrics Service
# =============================================================================


class BillingMetricsService:
    """Service for tracking billing metrics via structured logging."""

    @staticmethod
    def track_checkout_created(owner_type: str, plan: str) -> None:
        """Track checkout session creation."""
        logger.info(
            "billing_metric: checkout_created",
            extra={
                "metric_type": "counter",
                "metric_name": "billing_checkouts_created_total",
                "owner_type": owner_type,
                "plan": plan,
            },
        )

    @staticmethod
    def track_payment_succeeded(owner_type: str, plan: str, amount_cents: int) -> None:
        """Track successful payment."""
        logger.info(
            "billing_metric: payment_succeeded",
            extra={
                "metric_type": "counter",
                "metric_name": "billing_payments_succeeded_total",
                "owner_type": owner_type,
                "plan": plan,
                "amount_cents": amount_cents,
            },
        )

    @staticmethod
    def track_payment_failed(owner_type: str, reason: str) -> None:
        """Track failed payment."""
        logger.warning(
            "billing_metric: payment_failed",
            extra={
                "metric_type": "counter",
                "metric_name": "billing_payments_failed_total",
                "owner_type": owner_type,
                "reason": reason,
            },
        )

    @staticmethod
    def track_refund_issued(reason_category: str) -> None:
        """Track refund issued."""
        logger.info(
            "billing_metric: refund_issued",
            extra={
                "metric_type": "counter",
                "metric_name": "billing_refunds_issued_total",
                "reason_category": reason_category,
            },
        )

    @staticmethod
    def track_subscription_cancelled(owner_type: str, cancelled_by: str) -> None:
        """Track subscription cancellation."""
        logger.info(
            "billing_metric: subscription_cancelled",
            extra={
                "metric_type": "counter",
                "metric_name": "billing_subscriptions_cancelled_total",
                "owner_type": owner_type,
                "cancelled_by": cancelled_by,
            },
        )

    # =========================================================================
    # Proxy Billing Metrics
    # =========================================================================

    @staticmethod
    def track_billing_manager_assigned(assigned_by_type: str) -> None:
        """Track billing manager assignment (assigned_by_type: patient, proxy, admin)."""
        logger.info(
            "billing_metric: billing_manager_assigned",
            extra={
                "metric_type": "counter",
                "metric_name": "billing_manager_assignments_total",
                "assigned_by_type": assigned_by_type,
            },
        )

    @staticmethod
    def track_proxy_action(action_type: str) -> None:
        """Track proxy billing action (action_type: checkout, cancel, view)."""
        logger.info(
            "billing_metric: proxy_action",
            extra={
                "metric_type": "counter",
                "metric_name": "billing_proxy_actions_total",
                "action_type": action_type,
            },
        )

    @staticmethod
    def track_webhook_duration(event_type: str, duration_seconds: float) -> None:
        """Track webhook processing duration."""
        logger.info(
            "billing_metric: webhook_duration",
            extra={
                "metric_type": "histogram",
                "metric_name": "billing_webhook_processing_seconds",
                "event_type": event_type,
                "duration_seconds": duration_seconds,
            },
        )


# Singleton instance for convenience
billing_metrics = BillingMetricsService()
