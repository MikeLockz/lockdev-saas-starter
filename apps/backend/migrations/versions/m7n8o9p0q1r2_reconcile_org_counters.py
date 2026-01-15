"""Reconcile organization counter values.

Revision ID: m7n8o9p0q1r2
Revises: l6m7n8o9p0q1
Create Date: 2026-01-14

This migration reconciles the denormalized member_count and patient_count
fields on organizations table with the actual counts from the relationship tables.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "m7n8o9p0q1r2"
down_revision = "l6m7n8o9p0q1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Reconcile member_count with actual membership count
    # Only counts active (non-soft-deleted) members
    op.execute("""
        UPDATE organizations
        SET member_count = COALESCE((
            SELECT COUNT(*)
            FROM organization_memberships
            WHERE organization_memberships.organization_id = organizations.id
              AND organization_memberships.deleted_at IS NULL
        ), 0)
    """)

    # Reconcile patient_count with actual enrolled patients
    op.execute("""
        UPDATE organizations
        SET patient_count = COALESCE((
            SELECT COUNT(*)
            FROM organization_patients
            WHERE organization_patients.organization_id = organizations.id
        ), 0)
    """)


def downgrade() -> None:
    # No downgrade needed - the counts will be maintained by event listeners
    # and can be re-reconciled by running upgrade again if needed
    pass
