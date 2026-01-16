"""add unique primary provider constraint

Revision ID: 20260114_unique_primary
Revises: 20260114_rls_coverage
Create Date: 2026-01-14 22:00:00.000000

This migration adds a partial unique index to enforce the business rule:
"Only ONE provider can be marked as primary per patient per organization"

CRITICAL: This constraint prevents data integrity violations where multiple
providers could accidentally be designated as the primary care provider.

Related Documentation:
- docs/04 - sql.ddl (schema reference)
- docs/01 - Review prompt.md (requirement: FR-04)

Implementation Details:
- Uses PostgreSQL partial unique index (WHERE clause filtering)
- Only indexes rows where is_primary_provider = TRUE
- Allows unlimited non-primary providers per patient
- Handles existing duplicate data by keeping the earliest assignment
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260114_unique_primary'
down_revision = '20260114_rls_coverage'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add partial unique index to enforce one primary provider per patient.

    Steps:
    1. Identify and fix any existing violations (keep earliest assignment)
    2. Create the partial unique index
    """

    # ==========================================
    # STEP 1: Clean up existing duplicate primary providers
    # ==========================================
    # This UPDATE sets is_primary_provider=FALSE for all but the FIRST
    # primary provider per (organization_id, patient_id) based on assigned_at.
    #
    # Why this is safe:
    # - Uses DISTINCT ON to pick the earliest assignment per patient
    # - Only affects rows where is_primary_provider=TRUE
    # - Preserves all care team relationships (no data deletion)
    op.execute("""
        UPDATE care_team_assignments cta
        SET is_primary_provider = FALSE
        WHERE is_primary_provider = TRUE
        AND id NOT IN (
            SELECT DISTINCT ON (organization_id, patient_id) id
            FROM care_team_assignments
            WHERE is_primary_provider = TRUE
            ORDER BY organization_id, patient_id, assigned_at ASC
        );
    """)

    # ==========================================
    # STEP 2: Create partial unique index
    # ==========================================
    # Enforces uniqueness on (organization_id, patient_id)
    # ONLY when is_primary_provider = TRUE
    #
    # Benefits:
    # - Database-level enforcement (prevents application bugs)
    # - Minimal performance overhead (only indexes TRUE values)
    # - Allows unlimited non-primary providers
    op.create_index(
        'idx_unique_primary_provider_per_patient',
        'care_team_assignments',
        ['organization_id', 'patient_id'],
        unique=True,
        postgresql_where=sa.text('is_primary_provider = TRUE')
    )

    # Add comment to document the constraint
    op.execute("""
        COMMENT ON INDEX idx_unique_primary_provider_per_patient IS
        'Enforces business rule: Only ONE provider can be primary per patient per organization. Partial index only applies where is_primary_provider=TRUE.';
    """)


def downgrade() -> None:
    """
    Remove the unique constraint.

    WARNING: Removing this constraint may allow data integrity violations.
    Only downgrade if you have a compensating control in the application layer.
    """
    op.drop_index(
        'idx_unique_primary_provider_per_patient',
        table_name='care_team_assignments'
    )
