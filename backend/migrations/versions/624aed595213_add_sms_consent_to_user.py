"""add_sms_consent_to_user

Revision ID: 624aed595213
Revises: 0a6fde9a7ba6
Create Date: 2026-01-16 22:05:58.142085

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "624aed595213"
down_revision: str | Sequence[str] | None = "0a6fde9a7ba6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "communication_consent_sms",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.alter_column("users", "communication_consent_sms", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "communication_consent_sms")
