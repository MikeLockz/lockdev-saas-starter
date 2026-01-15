"""Merge heads

Revision ID: 72a31602b74c
Revises: 2b190a1ca083, l6m7n8o9p0q1
Create Date: 2026-01-12 15:32:21.506972

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "72a31602b74c"
down_revision: str | Sequence[str] | None = ("2b190a1ca083", "l6m7n8o9p0q1")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
