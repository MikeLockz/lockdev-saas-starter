"""add_timezone_fields

Revision ID: i3j4k5l6m7n8
Revises: h2i3j4k5l6m7
Create Date: 2026-01-04 12:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'i3j4k5l6m7n8'
down_revision: Union[str, Sequence[str], None] = 'h2i3j4k5l6m7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add timezone columns to organizations and users tables."""
    # Add timezone to organizations with default value
    op.add_column(
        'organizations',
        sa.Column('timezone', sa.String(50), nullable=False, server_default='America/New_York')
    )
    
    # Add timezone to users (nullable - uses org default if null)
    op.add_column(
        'users',
        sa.Column('timezone', sa.String(50), nullable=True)
    )


def downgrade() -> None:
    """Remove timezone columns."""
    op.drop_column('users', 'timezone')
    op.drop_column('organizations', 'timezone')
