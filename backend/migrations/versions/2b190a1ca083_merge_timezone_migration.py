"""merge_timezone_migration

Revision ID: 2b190a1ca083
Revises: dd4222bcd586, i3j4k5l6m7n8
Create Date: 2026-01-04 20:14:02.937673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b190a1ca083'
down_revision: Union[str, Sequence[str], None] = ('dd4222bcd586', 'i3j4k5l6m7n8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
