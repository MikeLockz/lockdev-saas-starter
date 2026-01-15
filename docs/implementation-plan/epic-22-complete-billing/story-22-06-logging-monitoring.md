# Story 22.6: Billing Logging & Monitoring
**User Story:** As a Developer/Admin, I want comprehensive logging and monitoring for all billing operations, so that I can track issues and audit all financial transactions.

## Status
- [x] **Complete**

## Context
- **Epic:** Epic 22 - Complete Billing & Subscription Management
- **Dependencies:**
  - All previous stories (22.1 - 22.5)
- **Existing Code:**
  - `backend/src/models/audit.py` - Audit log model
  - `backend/src/services/audit.py` - Audit service

## Technical Specification
**Goal:** Implement comprehensive logging, monitoring, and alerting for all billing operations.

### Changes Required

#### 1. Enhanced Audit Log Model: `backend/src/models/audit.py` (EXTEND)
```python
# Add billing-specific audit event types

class AuditEventType:
    # Existing types...

    # Billing Events
    BILLING_CHECKOUT_CREATED = "billing.checkout.created"
    BILLING_SUBSCRIPTION_CREATED = "billing.subscription.created"
    BILLING_SUBSCRIPTION_UPDATED = "billing.subscription.updated"
    BILLING_SUBSCRIPTION_CANCELLED = "billing.subscription.cancelled"
    BILLING_PAYMENT_SUCCEEDED = "billing.payment.succeeded"
    BILLING_PAYMENT_FAILED = "billing.payment.failed"
    BILLING_REFUND_ISSUED = "billing.refund.issued"
    BILLING_FREE_SUBSCRIPTION_GRANTED = "billing.free_subscription.granted"
    BILLING_OVERRIDE_CREATED = "billing.override.created"
    BILLING_OVERRIDE_REVOKED = "billing.override.revoked"
    BILLING_PORTAL_ACCESSED = "billing.portal.accessed"
    BILLING_WEBHOOK_RECEIVED = "billing.webhook.received"
    BILLING_WEBHOOK_FAILED = "billing.webhook.failed"

    # NEW: Proxy Billing Events
    BILLING_MANAGER_ASSIGNED = "billing.manager.assigned"
    BILLING_MANAGER_REMOVED = "billing.manager.removed"
    BILLING_PROXY_CHECKOUT_CREATED = "billing.proxy.checkout.created"
    BILLING_PROXY_SUBSCRIPTION_CANCELLED = "billing.proxy.subscription.cancelled"
```

#### 2. Billing Audit Service: `backend/src/services/billing_audit.py` (NEW)
```python
from ..models.audit import AuditLog, AuditEventType
from ..database import AsyncSession
from datetime import datetime
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class BillingAuditService:
    """Service for auditing billing operations"""

    @staticmethod
    async def log_checkout_created(
        db: AsyncSession,
        user_id: UUID,
        owner_id: UUID,
        owner_type: str,
        price_id: str,
        session_id: str,
        metadata: dict | None = None
    ):
        """Log checkout session creation"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_CHECKOUT_CREATED,
            user_id=user_id,
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action="create_checkout",
            metadata={
                "price_id": price_id,
                "session_id": session_id,
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            f"Checkout created: user={user_id}, owner={owner_id}, "
            f"owner_type={owner_type}, price={price_id}"
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
        metadata: dict | None = None
    ):
        """Log successful payment"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_PAYMENT_SUCCEEDED,
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action="payment_succeeded",
            metadata={
                "amount_cents": amount_cents,
                "currency": currency,
                "transaction_id": str(transaction_id),
                "stripe_invoice_id": stripe_invoice_id,
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            f"Payment succeeded: owner={owner_id}, amount={amount_cents}, "
            f"currency={currency}, invoice={stripe_invoice_id}"
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
        metadata: dict | None = None
    ):
        """Log failed payment"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_PAYMENT_FAILED,
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action="payment_failed",
            metadata={
                "amount_cents": amount_cents,
                "currency": currency,
                "reason": reason,
                "attempt_count": attempt_count,
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.warning(
            f"Payment failed: owner={owner_id}, amount={amount_cents}, "
            f"reason={reason}, attempt={attempt_count}"
        )

    @staticmethod
    async def log_refund_issued(
        db: AsyncSession,
        user_id: UUID,
        transaction_id: UUID,
        amount_cents: int,
        reason: str,
        refund_id: str,
        metadata: dict | None = None
    ):
        """Log refund issuance"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_REFUND_ISSUED,
            user_id=user_id,
            resource_type="transaction",
            resource_id=transaction_id,
            action="issue_refund",
            metadata={
                "amount_cents": amount_cents,
                "reason": reason,
                "refund_id": refund_id,
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.warning(
            f"Refund issued: admin={user_id}, transaction={transaction_id}, "
            f"amount={amount_cents}, reason={reason}"
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
        metadata: dict | None = None
    ):
        """Log free subscription grant"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_FREE_SUBSCRIPTION_GRANTED,
            user_id=user_id,
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action="grant_free_subscription",
            metadata={
                "reason": reason,
                "duration_months": duration_months,
                "override_id": str(override_id),
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            f"Free subscription granted: admin={user_id}, owner={owner_id}, "
            f"duration={duration_months}, reason={reason}"
        )

    @staticmethod
    async def log_subscription_cancelled(
        db: AsyncSession,
        user_id: UUID | None,
        owner_id: UUID,
        owner_type: str,
        reason: str | None,
        cancelled_immediately: bool,
        metadata: dict | None = None
    ):
        """Log subscription cancellation"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_SUBSCRIPTION_CANCELLED,
            user_id=user_id,
            resource_type=owner_type.lower(),
            resource_id=owner_id,
            action="cancel_subscription",
            metadata={
                "reason": reason,
                "cancelled_immediately": cancelled_immediately,
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            f"Subscription cancelled: user={user_id}, owner={owner_id}, "
            f"immediate={cancelled_immediately}, reason={reason}"
        )

    @staticmethod
    async def log_webhook_received(
        db: AsyncSession,
        event_type: str,
        event_id: str,
        customer_id: str | None,
        processed_successfully: bool,
        error: str | None = None,
        metadata: dict | None = None
    ):
        """Log webhook receipt"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_WEBHOOK_RECEIVED if processed_successfully
                       else AuditEventType.BILLING_WEBHOOK_FAILED,
            resource_type="webhook",
            action=event_type,
            metadata={
                "event_id": event_id,
                "customer_id": customer_id,
                "error": error,
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        if processed_successfully:
            logger.info(f"Webhook processed: type={event_type}, id={event_id}")
        else:
            logger.error(f"Webhook failed: type={event_type}, id={event_id}, error={error}")

    # NEW: Proxy Billing Audit Methods

    @staticmethod
    async def log_billing_manager_assigned(
        db: AsyncSession,
        patient_id: UUID,
        proxy_user_id: UUID,
        assigned_by: UUID,
        metadata: dict | None = None
    ):
        """Log billing manager assignment"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_MANAGER_ASSIGNED,
            user_id=assigned_by,
            resource_type="patient",
            resource_id=patient_id,
            action="assign_billing_manager",
            metadata={
                "proxy_user_id": str(proxy_user_id),
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            f"Billing manager assigned: patient={patient_id}, "
            f"proxy={proxy_user_id}, assigned_by={assigned_by}"
        )

    @staticmethod
    async def log_billing_manager_removed(
        db: AsyncSession,
        patient_id: UUID,
        proxy_user_id: UUID,
        removed_by: UUID,
        metadata: dict | None = None
    ):
        """Log billing manager removal"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_MANAGER_REMOVED,
            user_id=removed_by,
            resource_type="patient",
            resource_id=patient_id,
            action="remove_billing_manager",
            metadata={
                "proxy_user_id": str(proxy_user_id),
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            f"Billing manager removed: patient={patient_id}, "
            f"proxy={proxy_user_id}, removed_by={removed_by}"
        )

    @staticmethod
    async def log_proxy_checkout_created(
        db: AsyncSession,
        proxy_user_id: UUID,
        patient_id: UUID,
        price_id: str,
        session_id: str,
        metadata: dict | None = None
    ):
        """Log proxy-initiated checkout"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_PROXY_CHECKOUT_CREATED,
            user_id=proxy_user_id,
            resource_type="patient",
            resource_id=patient_id,
            action="proxy_create_checkout",
            metadata={
                "price_id": price_id,
                "session_id": session_id,
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            f"Proxy checkout created: proxy={proxy_user_id}, "
            f"patient={patient_id}, price={price_id}"
        )

    @staticmethod
    async def log_proxy_subscription_cancelled(
        db: AsyncSession,
        proxy_user_id: UUID,
        patient_id: UUID,
        reason: str | None,
        metadata: dict | None = None
    ):
        """Log proxy-initiated subscription cancellation"""
        audit = AuditLog(
            event_type=AuditEventType.BILLING_PROXY_SUBSCRIPTION_CANCELLED,
            user_id=proxy_user_id,
            resource_type="patient",
            resource_id=patient_id,
            action="proxy_cancel_subscription",
            metadata={
                "reason": reason,
                **(metadata or {})
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            f"Proxy cancelled subscription: proxy={proxy_user_id}, "
            f"patient={patient_id}, reason={reason}"
        )

billing_audit = BillingAuditService()
```

#### 3. Metrics Tracking: `backend/src/services/billing_metrics.py` (NEW)
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Counters
billing_checkouts_created = Counter(
    'billing_checkouts_created_total',
    'Total number of checkout sessions created',
    ['owner_type', 'plan']
)

billing_payments_succeeded = Counter(
    'billing_payments_succeeded_total',
    'Total number of successful payments',
    ['owner_type', 'plan']
)

billing_payments_failed = Counter(
    'billing_payments_failed_total',
    'Total number of failed payments',
    ['owner_type', 'reason']
)

billing_refunds_issued = Counter(
    'billing_refunds_issued_total',
    'Total number of refunds issued',
    ['reason_category']
)

billing_subscriptions_cancelled = Counter(
    'billing_subscriptions_cancelled_total',
    'Total number of subscriptions cancelled',
    ['owner_type', 'cancelled_by']
)

# NEW: Proxy Billing Counters
billing_manager_assignments = Counter(
    'billing_manager_assignments_total',
    'Total number of billing manager assignments',
    ['assigned_by_type']
)

billing_proxy_actions = Counter(
    'billing_proxy_actions_total',
    'Total number of proxy billing actions',
    ['action_type']
)

# Gauges
active_subscriptions = Gauge(
    'billing_active_subscriptions',
    'Number of currently active subscriptions',
    ['owner_type', 'plan']
)

monthly_recurring_revenue = Gauge(
    'billing_mrr_cents',
    'Monthly Recurring Revenue in cents',
    ['owner_type']
)

# NEW: Proxy Billing Gauge
proxy_managed_subscriptions = Gauge(
    'billing_proxy_managed_subscriptions',
    'Number of subscriptions managed by proxies',
    []
)

# Histograms
webhook_processing_duration = Histogram(
    'billing_webhook_processing_seconds',
    'Time spent processing webhooks',
    ['event_type']
)

payment_amount_distribution = Histogram(
    'billing_payment_amount_cents',
    'Distribution of payment amounts',
    ['owner_type'],
    buckets=[1000, 2000, 5000, 10000, 20000, 50000, 100000]
)

class BillingMetricsService:
    """Service for tracking billing metrics"""

    @staticmethod
    def track_checkout_created(owner_type: str, plan: str):
        billing_checkouts_created.labels(owner_type=owner_type, plan=plan).inc()

    @staticmethod
    def track_payment_succeeded(owner_type: str, plan: str, amount_cents: int):
        billing_payments_succeeded.labels(owner_type=owner_type, plan=plan).inc()
        payment_amount_distribution.labels(owner_type=owner_type).observe(amount_cents)

    @staticmethod
    def track_payment_failed(owner_type: str, reason: str):
        billing_payments_failed.labels(owner_type=owner_type, reason=reason).inc()

    @staticmethod
    def track_refund_issued(reason_category: str):
        billing_refunds_issued.labels(reason_category=reason_category).inc()

    @staticmethod
    def track_subscription_cancelled(owner_type: str, cancelled_by: str):
        billing_subscriptions_cancelled.labels(
            owner_type=owner_type,
            cancelled_by=cancelled_by
        ).inc()

    @staticmethod
    def update_active_subscriptions(owner_type: str, plan: str, count: int):
        active_subscriptions.labels(owner_type=owner_type, plan=plan).set(count)

    @staticmethod
    def update_mrr(owner_type: str, mrr_cents: int):
        monthly_recurring_revenue.labels(owner_type=owner_type).set(mrr_cents)

    @staticmethod
    def track_webhook_duration(event_type: str, duration_seconds: float):
        webhook_processing_duration.labels(event_type=event_type).observe(duration_seconds)

    # NEW: Proxy Billing Metrics Methods

    @staticmethod
    def track_billing_manager_assigned(assigned_by_type: str):
        """Track billing manager assignment (assigned_by_type: patient, proxy, admin)"""
        billing_manager_assignments.labels(assigned_by_type=assigned_by_type).inc()

    @staticmethod
    def track_proxy_action(action_type: str):
        """Track proxy billing action (action_type: checkout, cancel, view)"""
        billing_proxy_actions.labels(action_type=action_type).inc()

    @staticmethod
    def update_proxy_managed_count(count: int):
        """Update count of proxy-managed subscriptions"""
        proxy_managed_subscriptions.set(count)

billing_metrics = BillingMetricsService()
```

#### 4. Error Alerting: `backend/src/services/billing_alerts.py` (NEW)
```python
import logging
from enum import Enum
from ..services.email import send_email
from ..config import settings

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class BillingAlertsService:
    """Service for sending billing alerts"""

    @staticmethod
    async def alert_payment_failed(
        owner_email: str,
        owner_name: str,
        amount_cents: int,
        reason: str,
        attempt_count: int
    ):
        """Alert on payment failure"""
        if attempt_count >= 3:
            # Send alert to admins on final failure
            await BillingAlertsService._send_admin_alert(
                severity=AlertSeverity.ERROR,
                subject=f"Final Payment Failure: {owner_name}",
                message=f"""
                Payment failed after 3 attempts:
                - Customer: {owner_name} ({owner_email})
                - Amount: ${amount_cents / 100:.2f}
                - Reason: {reason}
                - Action: Subscription will be cancelled
                """
            )

    @staticmethod
    async def alert_webhook_failure(
        event_type: str,
        event_id: str,
        error: str
    ):
        """Alert on webhook processing failure"""
        await BillingAlertsService._send_admin_alert(
            severity=AlertSeverity.CRITICAL,
            subject=f"Webhook Processing Failed: {event_type}",
            message=f"""
            Failed to process Stripe webhook:
            - Event Type: {event_type}
            - Event ID: {event_id}
            - Error: {error}
            - Action: Manual investigation required
            """
        )

    @staticmethod
    async def alert_high_churn_rate(churn_rate: float):
        """Alert on abnormally high churn rate"""
        if churn_rate > 0.05:  # 5% monthly churn
            await BillingAlertsService._send_admin_alert(
                severity=AlertSeverity.WARNING,
                subject=f"High Churn Rate Detected: {churn_rate * 100:.1f}%",
                message=f"""
                Monthly churn rate is abnormally high:
                - Current churn: {churn_rate * 100:.1f}%
                - Threshold: 5.0%
                - Action: Review cancellation reasons and customer feedback
                """
            )

    @staticmethod
    async def alert_unusual_refund_activity(refund_count_today: int):
        """Alert on unusual refund activity"""
        if refund_count_today > 5:
            await BillingAlertsService._send_admin_alert(
                severity=AlertSeverity.WARNING,
                subject=f"Unusual Refund Activity: {refund_count_today} refunds today",
                message=f"""
                High number of refunds issued today:
                - Count: {refund_count_today}
                - Threshold: 5
                - Action: Review refund reasons for patterns
                """
            )

    @staticmethod
    async def _send_admin_alert(
        severity: AlertSeverity,
        subject: str,
        message: str
    ):
        """Send alert to admin team"""
        logger.log(
            logging.ERROR if severity == AlertSeverity.CRITICAL else logging.WARNING,
            f"[{severity.upper()}] {subject}"
        )

        # Send email to admin team
        if settings.BILLING_ALERT_EMAILS:
            for admin_email in settings.BILLING_ALERT_EMAILS.split(','):
                try:
                    await send_email(
                        to_email=admin_email.strip(),
                        subject=f"[{severity.upper()}] {subject}",
                        html_content=f"""
                        <html>
                        <body style="font-family: monospace;">
                        <h2 style="color: {'red' if severity == AlertSeverity.CRITICAL else 'orange'};">
                            Billing Alert: {severity.upper()}
                        </h2>
                        <pre>{message}</pre>
                        <p>
                        <small>Timestamp: {datetime.utcnow().isoformat()}</small>
                        </p>
                        </body>
                        </html>
                        """
                    )
                except Exception as e:
                    logger.error(f"Failed to send alert email: {e}")

billing_alerts = BillingAlertsService()
```

#### 5. Integration: Update all billing endpoints and webhooks
```python
# In billing.py, webhooks.py, etc. - add audit logging

# Example in webhooks.py:
async def _handle_payment_succeeded(event: dict, db: AsyncSession):
    start_time = time.time()

    try:
        # Existing logic...

        # Add audit logging
        await billing_audit.log_payment_succeeded(...)

        # Add metrics
        billing_metrics.track_payment_succeeded(...)

        # Track webhook duration
        duration = time.time() - start_time
        billing_metrics.track_webhook_duration("invoice.payment_succeeded", duration)

    except Exception as e:
        # Log webhook failure
        await billing_audit.log_webhook_received(
            db=db,
            event_type=event["type"],
            event_id=event["id"],
            customer_id=event["data"]["object"].get("customer"),
            processed_successfully=False,
            error=str(e)
        )

        # Send alert
        await billing_alerts.alert_webhook_failure(
            event_type=event["type"],
            event_id=event["id"],
            error=str(e)
        )

        raise
```

#### 6. Configuration: `backend/src/config.py` (EXTEND)
```python
# Add monitoring/alerting config
BILLING_ALERT_EMAILS: str = Field(default="")  # Comma-separated
ENABLE_BILLING_METRICS: bool = Field(default=True)
ENABLE_BILLING_ALERTS: bool = Field(default=True)
```

#### 7. Scheduled Jobs: `backend/src/tasks/billing_monitoring.py` (NEW)
```python
from celery import Celery
from celery.schedules import crontab

@celery.task
async def calculate_daily_metrics():
    """Calculate and update billing metrics daily"""
    # Calculate churn rate
    # Update MRR gauges
    # Check for unusual activity
    # Send daily billing report
    pass

@celery.task
async def check_billing_anomalies():
    """Check for billing anomalies every hour"""
    # High refund rate
    # Unusual cancellation patterns
    # Payment failure spikes
    pass

# Schedule tasks
celery.conf.beat_schedule = {
    'daily-billing-metrics': {
        'task': 'tasks.billing_monitoring.calculate_daily_metrics',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'hourly-billing-checks': {
        'task': 'tasks.billing_monitoring.check_billing_anomalies',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

## Acceptance Criteria
### General Billing Audit
- [ ] All billing API calls logged to audit table.
- [ ] Payment success/failure logged with details.
- [ ] Refunds logged with admin actor and reason.
- [ ] Webhook events logged with processing status.
- [ ] All logs include timestamps and actor IDs.
- [ ] Sensitive data (card numbers) never logged.

### Proxy Billing Audit
- [ ] Billing manager assignments logged with assigner ID.
- [ ] Billing manager removals logged with remover ID.
- [ ] Proxy-initiated checkouts logged with proxy user ID.
- [ ] Proxy-initiated cancellations logged with proxy user ID.

### Metrics
- [ ] Prometheus metrics exported for all key events.
- [ ] Proxy billing actions tracked separately.
- [ ] Billing manager assignments counted.
- [ ] Proxy-managed subscriptions gauge updated.

### Alerts
- [ ] Alerts sent on payment failures (3rd attempt).
- [ ] Alerts sent on webhook processing failures.
- [ ] Alerts sent on high churn rate.
- [ ] Alerts sent on unusual refund activity.
- [ ] Daily metrics calculated and reported.

## Verification Plan
**Automated Tests:**
```bash
pytest tests/services/test_billing_audit.py -v
pytest tests/services/test_billing_metrics.py -v
pytest tests/services/test_billing_alerts.py -v
```

**Test Cases:**
1. Test audit log creation for each billing event
2. Test metrics increment on events
3. Test alert triggering on failures
4. Test webhook failure logging
5. Test sensitive data redaction
6. Test billing manager assignment audit logging
7. Test billing manager removal audit logging
8. Test proxy checkout audit logging
9. Test proxy cancellation audit logging
10. Test proxy billing metrics tracking

**Manual Verification:**
1. Trigger payment success webhook
2. Check audit log entry created
3. Check Prometheus metrics updated
4. Trigger payment failure webhook
5. Verify alert email sent
6. Check logs for sensitive data leaks
7. Assign billing manager as admin
8. Verify billing manager assignment audit log
9. Proxy creates checkout for patient
10. Verify proxy checkout audit log with proxy user ID
11. Check proxy billing metrics updated
12. View Grafana dashboards (if available)

## Monitoring Dashboard
Create Grafana dashboards for:
- **Revenue Metrics**: MRR, ARPU, total revenue
- **Subscription Metrics**: Active, new, cancelled, churn rate
- **Payment Metrics**: Success rate, failure reasons
- **Webhook Metrics**: Processing time, failure rate
- **Refund Metrics**: Count, reasons, amounts
- **Proxy Billing Metrics**: Proxy-managed subscriptions, billing manager assignments, proxy actions

## Security Considerations
- [ ] Never log full credit card numbers
- [ ] Never log CVV or security codes
- [ ] Redact sensitive Stripe tokens
- [ ] Restrict audit log access to admins only
- [ ] Encrypt audit logs at rest
- [ ] Rotate logs periodically
- [ ] Comply with PCI-DSS logging requirements

## Rollback Plan
If issues arise:
1. Disable metrics collection via feature flag
2. Disable alert emails via config
3. Continue basic logging only
4. Fix issues in staging
5. Re-enable gradually
