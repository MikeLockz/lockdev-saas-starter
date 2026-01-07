"""Add contact_methods table with trigram indexes for patients

Revision ID: d4e5f6a7b8c9
Revises: be1ec14586f6
Create Date: 2026-01-02

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "be1ec14586f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Enable pg_trgm extension for fuzzy text search (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Create contact_methods table
    op.create_table(
        "contact_methods",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_safe_for_voicemail", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("label", sa.String(50), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
        ),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_contact_methods_patient", "contact_methods", ["patient_id"])

    # Add trigram indexes for patients fuzzy search
    op.create_index(
        "idx_patients_last_name_trgm",
        "patients",
        ["last_name"],
        postgresql_using="gin",
        postgresql_ops={"last_name": "gin_trgm_ops"},
        if_not_exists=True,
    )
    op.create_index(
        "idx_patients_first_name_trgm",
        "patients",
        ["first_name"],
        postgresql_using="gin",
        postgresql_ops={"first_name": "gin_trgm_ops"},
        if_not_exists=True,
    )
    op.create_index(
        "idx_patients_mrn_trgm",
        "patients",
        ["medical_record_number"],
        postgresql_using="gin",
        postgresql_ops={"medical_record_number": "gin_trgm_ops"},
        if_not_exists=True,
    )

    # Standard indexes
    op.create_index("idx_patients_dob", "patients", ["dob"], if_not_exists=True)
    op.create_index("idx_patients_mrn", "patients", ["medical_record_number"], if_not_exists=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_patients_mrn", table_name="patients")
    op.drop_index("idx_patients_dob", table_name="patients")
    op.drop_index("idx_patients_mrn_trgm", table_name="patients")
    op.drop_index("idx_patients_first_name_trgm", table_name="patients")
    op.drop_index("idx_patients_last_name_trgm", table_name="patients")
    op.drop_index("idx_contact_methods_patient", table_name="contact_methods")

    # Drop table
    op.drop_table("contact_methods")
