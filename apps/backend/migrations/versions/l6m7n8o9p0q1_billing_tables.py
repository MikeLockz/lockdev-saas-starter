"""Add billing tables and patient billing_manager fields

Revision ID: l6m7n8o9p0q1
Revises: k5l6m7n8o9p0
Create Date: 2026-01-12 10:00:00.000000

Epic 22 - Complete Billing & Subscription Management
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision = "l6m7n8o9p0q1"
down_revision = "k5l6m7n8o9p0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add billing_manager fields to patients table
    op.add_column("patients", sa.Column("billing_manager_id", UUID(), nullable=True))
    op.add_column(
        "patients",
        sa.Column("billing_manager_assigned_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("patients", sa.Column("billing_manager_assigned_by", UUID(), nullable=True))

    # Create foreign keys for billing_manager fields
    op.create_foreign_key(
        "fk_patients_billing_manager_id_users",
        "patients",
        "users",
        ["billing_manager_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_patients_billing_manager_assigned_by_users",
        "patients",
        "users",
        ["billing_manager_assigned_by"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create index for billing_manager_id
    op.create_index(
        "ix_patients_billing_manager_id",
        "patients",
        ["billing_manager_id"],
        postgresql_where=sa.text("billing_manager_id IS NOT NULL"),
    )

    # Create billing_transactions table
    op.create_table(
        "billing_transactions",
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", UUID(), nullable=False),
        sa.Column("owner_type", sa.String(20), nullable=False),
        sa.Column("stripe_payment_intent_id", sa.String(100), nullable=True),
        sa.Column("stripe_invoice_id", sa.String(100), nullable=True),
        sa.Column("stripe_charge_id", sa.String(100), nullable=True),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="usd"),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("receipt_url", sa.String(500), nullable=True),
        sa.Column("receipt_number", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refunded_by", UUID(), nullable=True),
        sa.Column("refund_reason", sa.Text(), nullable=True),
        sa.Column("managed_by_proxy_id", UUID(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["refunded_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["managed_by_proxy_id"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "owner_type IN ('PATIENT', 'ORGANIZATION')",
            name="ck_billing_transactions_owner_type",
        ),
        sa.CheckConstraint(
            "status IN ('SUCCEEDED', 'FAILED', 'REFUNDED', 'PENDING', 'CANCELLED')",
            name="ck_billing_transactions_status",
        ),
        sa.UniqueConstraint("stripe_payment_intent_id", name="uq_billing_transactions_payment_intent"),
    )

    # Create indexes for billing_transactions
    op.create_index(
        "ix_billing_transactions_owner",
        "billing_transactions",
        ["owner_id", "owner_type"],
    )
    op.create_index("ix_billing_transactions_status", "billing_transactions", ["status"])
    op.create_index(
        "ix_billing_transactions_created_at",
        "billing_transactions",
        ["created_at"],
        postgresql_ops={"created_at": "DESC"},
    )
    op.create_index(
        "ix_billing_transactions_stripe_pi",
        "billing_transactions",
        ["stripe_payment_intent_id"],
        postgresql_where=sa.text("stripe_payment_intent_id IS NOT NULL"),
    )
    op.create_index(
        "ix_billing_transactions_proxy",
        "billing_transactions",
        ["managed_by_proxy_id"],
        postgresql_where=sa.text("managed_by_proxy_id IS NOT NULL"),
    )

    # Create subscription_overrides table
    op.create_table(
        "subscription_overrides",
        sa.Column("id", UUID(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", UUID(), nullable=False),
        sa.Column("owner_type", sa.String(20), nullable=False),
        sa.Column("override_type", sa.String(30), nullable=False),
        sa.Column("granted_by", UUID(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("discount_percent", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_by", UUID(), nullable=True),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["granted_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["revoked_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "owner_type IN ('PATIENT', 'ORGANIZATION')",
            name="ck_subscription_overrides_owner_type",
        ),
        sa.CheckConstraint(
            "override_type IN ('FREE', 'TRIAL_EXTENSION', 'MANUAL_CANCEL', 'DISCOUNT')",
            name="ck_subscription_overrides_type",
        ),
        sa.CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100",
            name="ck_subscription_overrides_discount",
        ),
    )

    # Create indexes for subscription_overrides
    op.create_index(
        "ix_subscription_overrides_owner",
        "subscription_overrides",
        ["owner_id", "owner_type"],
    )
    op.create_index(
        "ix_subscription_overrides_active",
        "subscription_overrides",
        ["owner_id", "owner_type"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )


def downgrade() -> None:
    # Drop subscription_overrides indexes and table
    op.drop_index("ix_subscription_overrides_active", table_name="subscription_overrides")
    op.drop_index("ix_subscription_overrides_owner", table_name="subscription_overrides")
    op.drop_table("subscription_overrides")

    # Drop billing_transactions indexes and table
    op.drop_index("ix_billing_transactions_proxy", table_name="billing_transactions")
    op.drop_index("ix_billing_transactions_stripe_pi", table_name="billing_transactions")
    op.drop_index("ix_billing_transactions_created_at", table_name="billing_transactions")
    op.drop_index("ix_billing_transactions_status", table_name="billing_transactions")
    op.drop_index("ix_billing_transactions_owner", table_name="billing_transactions")
    op.drop_table("billing_transactions")

    # Drop patient billing_manager fields
    op.drop_index("ix_patients_billing_manager_id", table_name="patients")
    op.drop_constraint("fk_patients_billing_manager_assigned_by_users", "patients", type_="foreignkey")
    op.drop_constraint("fk_patients_billing_manager_id_users", "patients", type_="foreignkey")
    op.drop_column("patients", "billing_manager_assigned_by")
    op.drop_column("patients", "billing_manager_assigned_at")
    op.drop_column("patients", "billing_manager_id")
