"""
Billing Audit Service Tests

Tests for Story 22.6 - Billing Logging & Monitoring
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.billing_audit import (
    BillingAuditEventType,
    billing_audit,
)


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = AsyncMock(spec=AsyncSession)
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


class TestBillingAuditEventTypes:
    """Tests for BillingAuditEventType constants."""

    def test_checkout_event_type(self):
        assert BillingAuditEventType.CHECKOUT_CREATED == "billing.checkout.created"

    def test_payment_event_types(self):
        assert BillingAuditEventType.PAYMENT_SUCCEEDED == "billing.payment.succeeded"
        assert BillingAuditEventType.PAYMENT_FAILED == "billing.payment.failed"

    def test_subscription_event_types(self):
        assert BillingAuditEventType.SUBSCRIPTION_CREATED == "billing.subscription.created"
        assert BillingAuditEventType.SUBSCRIPTION_CANCELLED == "billing.subscription.cancelled"

    def test_admin_action_event_types(self):
        assert BillingAuditEventType.REFUND_ISSUED == "billing.refund.issued"
        assert BillingAuditEventType.FREE_SUBSCRIPTION_GRANTED == "billing.free_subscription.granted"

    def test_proxy_event_types(self):
        assert BillingAuditEventType.BILLING_MANAGER_ASSIGNED == "billing.manager.assigned"
        assert BillingAuditEventType.BILLING_MANAGER_REMOVED == "billing.manager.removed"
        assert BillingAuditEventType.PROXY_CHECKOUT_CREATED == "billing.proxy.checkout.created"


class TestBillingAuditService:
    """Tests for BillingAuditService methods."""

    @pytest.mark.asyncio
    async def test_log_checkout_created(self, mock_db):
        """Test logging checkout creation."""
        user_id = uuid.uuid4()
        owner_id = uuid.uuid4()

        await billing_audit.log_checkout_created(
            db=mock_db,
            user_id=user_id,
            owner_id=owner_id,
            owner_type="PATIENT",
            price_id="price_test123",
            session_id="cs_test123",
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        # Verify audit log was created
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.actor_user_id == user_id
        assert audit_log.resource_id == owner_id
        assert audit_log.resource_type == "patient"
        assert audit_log.action_type == "CREATE"
        assert "price_id" in audit_log.changes_json
        assert audit_log.changes_json["price_id"] == "price_test123"

    @pytest.mark.asyncio
    async def test_log_payment_succeeded(self, mock_db):
        """Test logging successful payment."""
        owner_id = uuid.uuid4()
        transaction_id = uuid.uuid4()

        await billing_audit.log_payment_succeeded(
            db=mock_db,
            owner_id=owner_id,
            owner_type="PATIENT",
            amount_cents=7900,
            currency="usd",
            transaction_id=transaction_id,
            stripe_invoice_id="in_test123",
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.changes_json["amount_cents"] == 7900
        assert audit_log.changes_json["currency"] == "usd"

    @pytest.mark.asyncio
    async def test_log_payment_failed(self, mock_db):
        """Test logging failed payment."""
        owner_id = uuid.uuid4()

        await billing_audit.log_payment_failed(
            db=mock_db,
            owner_id=owner_id,
            owner_type="PATIENT",
            amount_cents=7900,
            currency="usd",
            reason="card_declined",
            attempt_count=2,
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.changes_json["reason"] == "card_declined"
        assert audit_log.changes_json["attempt_count"] == 2

    @pytest.mark.asyncio
    async def test_log_refund_issued(self, mock_db):
        """Test logging refund issuance."""
        user_id = uuid.uuid4()
        transaction_id = uuid.uuid4()

        await billing_audit.log_refund_issued(
            db=mock_db,
            user_id=user_id,
            transaction_id=transaction_id,
            amount_cents=5000,
            reason="Customer request",
            refund_id="re_test123",
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.actor_user_id == user_id
        assert audit_log.resource_type == "transaction"
        assert audit_log.changes_json["reason"] == "Customer request"

    @pytest.mark.asyncio
    async def test_log_free_subscription_granted(self, mock_db):
        """Test logging free subscription grant."""
        user_id = uuid.uuid4()
        owner_id = uuid.uuid4()
        override_id = uuid.uuid4()

        await billing_audit.log_free_subscription_granted(
            db=mock_db,
            user_id=user_id,
            owner_id=owner_id,
            owner_type="PATIENT",
            reason="Promotional offer",
            duration_months=12,
            override_id=override_id,
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.changes_json["duration_months"] == 12
        assert audit_log.changes_json["reason"] == "Promotional offer"

    @pytest.mark.asyncio
    async def test_log_subscription_cancelled(self, mock_db):
        """Test logging subscription cancellation."""
        user_id = uuid.uuid4()
        owner_id = uuid.uuid4()

        await billing_audit.log_subscription_cancelled(
            db=mock_db,
            user_id=user_id,
            owner_id=owner_id,
            owner_type="PATIENT",
            reason="Customer request",
            cancelled_immediately=False,
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.changes_json["cancelled_immediately"] is False

    @pytest.mark.asyncio
    async def test_log_webhook_received_success(self, mock_db):
        """Test logging successful webhook processing."""
        await billing_audit.log_webhook_received(
            db=mock_db,
            event_type="invoice.payment_succeeded",
            event_id="evt_test123",
            customer_id="cus_test123",
            processed_successfully=True,
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.changes_json["event_type"] == BillingAuditEventType.WEBHOOK_RECEIVED

    @pytest.mark.asyncio
    async def test_log_webhook_received_failure(self, mock_db):
        """Test logging failed webhook processing."""
        await billing_audit.log_webhook_received(
            db=mock_db,
            event_type="invoice.payment_succeeded",
            event_id="evt_test123",
            customer_id="cus_test123",
            processed_successfully=False,
            error="Database error",
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.changes_json["event_type"] == BillingAuditEventType.WEBHOOK_FAILED
        assert audit_log.changes_json["error"] == "Database error"

    @pytest.mark.asyncio
    async def test_log_billing_manager_assigned(self, mock_db):
        """Test logging billing manager assignment."""
        patient_id = uuid.uuid4()
        proxy_user_id = uuid.uuid4()
        assigned_by = uuid.uuid4()

        await billing_audit.log_billing_manager_assigned(
            db=mock_db,
            patient_id=patient_id,
            proxy_user_id=proxy_user_id,
            assigned_by=assigned_by,
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.actor_user_id == assigned_by
        assert audit_log.resource_id == patient_id
        assert audit_log.changes_json["proxy_user_id"] == str(proxy_user_id)

    @pytest.mark.asyncio
    async def test_log_billing_manager_removed(self, mock_db):
        """Test logging billing manager removal."""
        patient_id = uuid.uuid4()
        proxy_user_id = uuid.uuid4()
        removed_by = uuid.uuid4()

        await billing_audit.log_billing_manager_removed(
            db=mock_db,
            patient_id=patient_id,
            proxy_user_id=proxy_user_id,
            removed_by=removed_by,
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.actor_user_id == removed_by

    @pytest.mark.asyncio
    async def test_log_proxy_checkout_created(self, mock_db):
        """Test logging proxy-initiated checkout."""
        proxy_user_id = uuid.uuid4()
        patient_id = uuid.uuid4()

        await billing_audit.log_proxy_checkout_created(
            db=mock_db,
            proxy_user_id=proxy_user_id,
            patient_id=patient_id,
            price_id="price_test123",
            session_id="cs_test123",
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.actor_user_id == proxy_user_id
        assert audit_log.resource_id == patient_id
        assert audit_log.changes_json["event_type"] == BillingAuditEventType.PROXY_CHECKOUT_CREATED

    @pytest.mark.asyncio
    async def test_log_proxy_subscription_cancelled(self, mock_db):
        """Test logging proxy-initiated subscription cancellation."""
        proxy_user_id = uuid.uuid4()
        patient_id = uuid.uuid4()

        await billing_audit.log_proxy_subscription_cancelled(
            db=mock_db,
            proxy_user_id=proxy_user_id,
            patient_id=patient_id,
            reason="Patient request",
        )

        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.changes_json["reason"] == "Patient request"
