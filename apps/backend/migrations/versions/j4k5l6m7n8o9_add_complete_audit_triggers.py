"""add_complete_audit_triggers

Revision ID: j4k5l6m7n8o9
Revises: i3j4k5l6m7n8
Create Date: 2026-01-11 21:10:00.000000

Adds audit triggers to remaining PHI tables for HIPAA compliance.
This addresses P0-004 from the security audit.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "j4k5l6m7n8o9"
down_revision: str | Sequence[str] | None = "i3j4k5l6m7n8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add audit triggers to remaining PHI-containing tables."""
    # Tables that need audit triggers but don't have them yet
    # These tables contain PHI or are critical for compliance
    tables = [
        "appointments",
        "documents",
        "care_team_assignments",
        "contact_methods",
        "providers",
        "staff",
        "user_sessions",
    ]

    for table in tables:
        # Use IF NOT EXISTS equivalent by checking first
        # Some tables might not exist in all deployments
        op.execute(f"""
        DO $$
        BEGIN
            -- Check if trigger already exists
            IF NOT EXISTS (
                SELECT 1 FROM pg_trigger
                WHERE tgname = 'audit_trigger_{table}'
            ) THEN
                -- Check if table exists before creating trigger
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = '{table}'
                ) THEN
                    CREATE TRIGGER audit_trigger_{table}
                    AFTER INSERT OR UPDATE OR DELETE ON {table}
                    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
                END IF;
            END IF;
        END $$;
        """)


def downgrade() -> None:
    """Remove audit triggers from the tables."""
    tables = [
        "appointments",
        "documents",
        "care_team_assignments",
        "contact_methods",
        "providers",
        "staff",
        "user_sessions",
    ]

    for table in tables:
        op.execute(f"DROP TRIGGER IF EXISTS audit_trigger_{table} ON {table}")
