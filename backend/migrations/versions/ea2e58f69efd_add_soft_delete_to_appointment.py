"""add_soft_delete_to_appointment

Revision ID: ea2e58f69efd
Revises: 624aed595213
Create Date: 2026-01-17 00:02:20.996129

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea2e58f69efd"
down_revision: str | Sequence[str] | None = "624aed595213"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "appointments",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("appointments", "deleted_at")
