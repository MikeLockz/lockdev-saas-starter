"""
Billing Alerts Service

Service for sending billing alerts on failures and anomalies.
Story 22.6 - Epic 22: Complete Billing & Subscription Management
"""

import logging
from datetime import datetime
from enum import Enum

from src.config import settings
from src.services.email import email_service

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BillingAlertsService:
    """Service for sending billing alerts."""

    @staticmethod
    async def alert_payment_failed(
        owner_email: str,
        owner_name: str,
        amount_cents: int,
        reason: str,
        attempt_count: int,
    ) -> None:
        """Alert on payment failure."""
        if attempt_count >= 3:
            # Send alert to admins on final failure
            await BillingAlertsService._send_admin_alert(
                severity=AlertSeverity.ERROR,
                subject=f"Final Payment Failure: {owner_name}",
                message=f"""
Payment failed after {attempt_count} attempts:
- Customer: {owner_name} ({owner_email})
- Amount: ${amount_cents / 100:.2f}
- Reason: {reason}
- Action: Subscription will be cancelled
                """.strip(),
            )

    @staticmethod
    async def alert_webhook_failure(
        event_type: str,
        event_id: str,
        error: str,
    ) -> None:
        """Alert on webhook processing failure."""
        await BillingAlertsService._send_admin_alert(
            severity=AlertSeverity.CRITICAL,
            subject=f"Webhook Processing Failed: {event_type}",
            message=f"""
Failed to process Stripe webhook:
- Event Type: {event_type}
- Event ID: {event_id}
- Error: {error}
- Action: Manual investigation required
            """.strip(),
        )

    @staticmethod
    async def alert_high_churn_rate(churn_rate: float) -> None:
        """Alert on abnormally high churn rate."""
        if churn_rate > 0.05:  # 5% monthly churn threshold
            await BillingAlertsService._send_admin_alert(
                severity=AlertSeverity.WARNING,
                subject=f"High Churn Rate Detected: {churn_rate * 100:.1f}%",
                message=f"""
Monthly churn rate is abnormally high:
- Current churn: {churn_rate * 100:.1f}%
- Threshold: 5.0%
- Action: Review cancellation reasons and customer feedback
                """.strip(),
            )

    @staticmethod
    async def alert_unusual_refund_activity(refund_count_today: int) -> None:
        """Alert on unusual refund activity."""
        if refund_count_today > 5:
            await BillingAlertsService._send_admin_alert(
                severity=AlertSeverity.WARNING,
                subject=f"Unusual Refund Activity: {refund_count_today} refunds today",
                message=f"""
High number of refunds issued today:
- Count: {refund_count_today}
- Threshold: 5
- Action: Review refund reasons for patterns
                """.strip(),
            )

    @staticmethod
    async def _send_admin_alert(
        severity: AlertSeverity,
        subject: str,
        message: str,
    ) -> None:
        """Send alert to admin team."""
        log_level = logging.ERROR if severity == AlertSeverity.CRITICAL else logging.WARNING
        logger.log(log_level, "[%s] %s: %s", severity.value.upper(), subject, message)

        # Get billing alert emails from settings
        billing_alert_emails = getattr(settings, "BILLING_ALERT_EMAILS", "")
        enable_billing_alerts = getattr(settings, "ENABLE_BILLING_ALERTS", True)

        if not enable_billing_alerts or not billing_alert_emails:
            return

        # Send email to admin team
        for admin_email in billing_alert_emails.split(","):
            admin_email = admin_email.strip()
            if not admin_email:
                continue
            try:
                severity_color = "red" if severity == AlertSeverity.CRITICAL else "orange"
                await email_service.send_email(
                    to_email=admin_email,
                    subject=f"[{severity.value.upper()}] {subject}",
                    template_name=None,  # Use raw HTML
                    html_content=f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: monospace; padding: 20px; }}
        h2 {{ color: {severity_color}; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h2>Billing Alert: {severity.value.upper()}</h2>
    <pre>{message}</pre>
    <p><small>Timestamp: {datetime.utcnow().isoformat()}</small></p>
</body>
</html>
                    """.strip(),
                )
            except Exception as e:
                logger.error("Failed to send alert email to %s: %s", admin_email, e)


# Singleton instance for convenience
billing_alerts = BillingAlertsService()
