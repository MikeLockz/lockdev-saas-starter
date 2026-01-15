"""Add unique constraint for PRIMARY provider per patient

Revision ID: n8o9p0q1r2s3
Revises: f81d44293b9a
Create Date: 2026-01-14

This migration adds a unique partial index to enforce the business rule that
only one provider can be assigned as PRIMARY per patient at any given time.

The constraint allows:
- Multiple SPECIALIST or CONSULTANT providers per patient
- Historical PRIMARY assignments (soft-deleted with removed_at set)
- Only ONE active PRIMARY provider per patient (removed_at IS NULL)

Before applying this migration, run check_primary_violations.sql to ensure
there are no existing violations in the database.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "n8o9p0q1r2s3"
down_revision: str | Sequence[str] | None = "f81d44293b9a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add unique partial index to enforce one PRIMARY provider per patient.

    The partial index applies only to active PRIMARY assignments, allowing:
    - Multiple providers with SPECIALIST or CONSULTANT roles
    - Multiple historical PRIMARY assignments (soft-deleted records)
    - Only one active PRIMARY provider per patient
    """
    op.create_index(
        "uq_care_team_primary",
        "care_team_assignments",
        ["patient_id"],
        unique=True,
        postgresql_where=sa.text("role = 'PRIMARY' AND removed_at IS NULL"),
    )


def downgrade() -> None:
    """Remove PRIMARY provider constraint.

    This allows multiple PRIMARY providers per patient, which violates
    the documented business rule but may be necessary for emergency rollback.
    """
    op.drop_index(
        "uq_care_team_primary",
        table_name="care_team_assignments",
    )
