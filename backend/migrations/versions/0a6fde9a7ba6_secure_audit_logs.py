"""secure_audit_logs

Revision ID: 0a6fde9a7ba6
Revises: ec20df1795df
Create Date: 2026-01-16 01:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0a6fde9a7ba6"
down_revision: str | Sequence[str] | None = "ec20df1795df"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Function to prevent modifications
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Audit logs are immutable';
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Trigger on audit_logs
    op.execute("""
        CREATE TRIGGER audit_logs_immutable
        BEFORE UPDATE OR DELETE ON audit_logs
        FOR EACH ROW
        EXECUTE PROCEDURE prevent_audit_log_modification();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS audit_logs_immutable ON audit_logs")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_log_modification")
