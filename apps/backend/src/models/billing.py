"""Billing models for transactions and subscription overrides."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin


class BillingTransaction(Base, UUIDMixin, TimestampMixin):
    """Records all billing transactions for patients and organizations."""

    __tablename__ = "billing_transactions"

    owner_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    owner_type: Mapped[str] = mapped_column(String(20), nullable=False)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    stripe_invoice_id: Mapped[str | None] = mapped_column(String(100))
    stripe_charge_id: Mapped[str | None] = mapped_column(String(100))
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="usd")
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    receipt_url: Mapped[str | None] = mapped_column(String(500))
    receipt_number: Mapped[str | None] = mapped_column(String(100))
    refunded_at: Mapped[datetime | None]
    refunded_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    refund_reason: Mapped[str | None] = mapped_column(Text)
    managed_by_proxy_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    metadata: Mapped[dict | None] = mapped_column(JSONB)

    # Relationships
    refunded_by_user: Mapped["User"] = relationship(foreign_keys=[refunded_by], lazy="joined")
    managed_by_proxy: Mapped["User"] = relationship(foreign_keys=[managed_by_proxy_id], lazy="joined")

    __table_args__ = (
        CheckConstraint("owner_type IN ('PATIENT', 'ORGANIZATION')", name="ck_billing_transactions_owner_type"),
        CheckConstraint(
            "status IN ('SUCCEEDED', 'FAILED', 'REFUNDED', 'PENDING', 'CANCELLED')",
            name="ck_billing_transactions_status",
        ),
        Index("ix_billing_transactions_owner", "owner_id", "owner_type"),
        Index("ix_billing_transactions_status", "status"),
        Index("ix_billing_transactions_created_at", "created_at", postgresql_ops={"created_at": "DESC"}),
        Index(
            "ix_billing_transactions_stripe_pi",
            "stripe_payment_intent_id",
            postgresql_where="stripe_payment_intent_id IS NOT NULL",
        ),
        Index(
            "ix_billing_transactions_proxy",
            "managed_by_proxy_id",
            postgresql_where="managed_by_proxy_id IS NOT NULL",
        ),
    )


class SubscriptionOverride(Base, UUIDMixin, TimestampMixin):
    """Administrative overrides for subscriptions (free, discounts, etc.)."""

    __tablename__ = "subscription_overrides"

    owner_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    owner_type: Mapped[str] = mapped_column(String(20), nullable=False)
    override_type: Mapped[str] = mapped_column(String(30), nullable=False)
    granted_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None]
    discount_percent: Mapped[int | None] = mapped_column(Integer)
    revoked_at: Mapped[datetime | None]
    revoked_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    metadata: Mapped[dict | None] = mapped_column(JSONB)

    # Relationships
    granted_by_user: Mapped["User"] = relationship(foreign_keys=[granted_by], lazy="joined")
    revoked_by_user: Mapped["User"] = relationship(foreign_keys=[revoked_by], lazy="joined")

    __table_args__ = (
        CheckConstraint("owner_type IN ('PATIENT', 'ORGANIZATION')", name="ck_subscription_overrides_owner_type"),
        CheckConstraint(
            "override_type IN ('FREE', 'TRIAL_EXTENSION', 'MANUAL_CANCEL', 'DISCOUNT')",
            name="ck_subscription_overrides_type",
        ),
        CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100",
            name="ck_subscription_overrides_discount",
        ),
        Index("ix_subscription_overrides_owner", "owner_id", "owner_type"),
        Index(
            "ix_subscription_overrides_active",
            "owner_id",
            "owner_type",
            postgresql_where="revoked_at IS NULL",
        ),
    )
