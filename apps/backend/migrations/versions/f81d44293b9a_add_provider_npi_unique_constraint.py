"""add_provider_npi_unique_constraint

Revision ID: f81d44293b9a
Revises: 5916bb71d4b8
Create Date: 2026-01-15 03:20:32.316264

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f81d44293b9a"
down_revision: str | Sequence[str] | None = "5916bb71d4b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add unique constraint on (organization_id, npi_number) to providers table.

    This ensures that NPI numbers are unique within each organization, preventing
    multiple providers in the same org from having the same NPI. The partial index
    excludes NULL values so providers without an NPI can still be created.
    """
    op.create_index(
        "ix_providers_org_npi_unique",
        "providers",
        ["organization_id", "npi_number"],
        unique=True,
        postgresql_where="npi_number IS NOT NULL",
    )


def downgrade() -> None:
    """Remove the NPI unique constraint."""
    op.drop_index("ix_providers_org_npi_unique", table_name="providers", postgresql_where="npi_number IS NOT NULL")
