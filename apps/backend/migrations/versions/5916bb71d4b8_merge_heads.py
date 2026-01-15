"""merge_heads

Revision ID: 5916bb71d4b8
Revises: 72a31602b74c, m7n8o9p0q1r2
Create Date: 2026-01-15 03:20:23.225401

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "5916bb71d4b8"
down_revision: str | Sequence[str] | None = ("72a31602b74c", "m7n8o9p0q1r2")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
