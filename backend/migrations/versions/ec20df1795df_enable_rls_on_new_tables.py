"""enable_rls_on_new_tables

Revision ID: ec20df1795df
Revises: 5d19c326cff3
Create Date: 2026-01-16 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec20df1795df"
down_revision: str | Sequence[str] | None = "5d19c326cff3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Simple Organization Scoped Tables
    # Includes original tables (patients, providers, staff, proxies) to ensure RLS is enforced
    tables_simple = [
        "patients",
        "providers",
        "staff",
        "proxies",
        "appointments",
        "documents",
        "tasks",
        "call_logs",
        "support_tickets",
        "invitations",
    ]
    for table in tables_simple:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        # Drop existing policy to avoid conflict if it exists
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"""
            CREATE POLICY tenant_isolation_{table} ON {table}
            USING (organization_id = current_setting('app.current_tenant_id', TRUE))
        """)

    # 2. Joined Scoped Tables
    # contact_methods
    op.execute("ALTER TABLE contact_methods ENABLE ROW LEVEL SECURITY")
    op.execute(
        "DROP POLICY IF EXISTS tenant_isolation_contact_methods ON contact_methods"
    )
    op.execute("""
        CREATE POLICY tenant_isolation_contact_methods ON contact_methods
        USING (
            EXISTS (
                SELECT 1 FROM patients
                WHERE patients.id = contact_methods.patient_id
                AND patients.organization_id = current_setting('app.current_tenant_id', TRUE)
            )
        )
    """)

    # care_team_assignments
    op.execute("ALTER TABLE care_team_assignments ENABLE ROW LEVEL SECURITY")
    op.execute(
        "DROP POLICY IF EXISTS tenant_isolation_care_team_assignments ON care_team_assignments"
    )
    op.execute("""
        CREATE POLICY tenant_isolation_care_team_assignments ON care_team_assignments
        USING (
            EXISTS (
                SELECT 1 FROM patients
                WHERE patients.id = care_team_assignments.patient_id
                AND patients.organization_id = current_setting('app.current_tenant_id', TRUE)
            )
        )
    """)

    # 3. Audit Triggers
    audit_tables = [
        "organizations",
        "users",
        "patients",
        "appointments",
        "documents",
        "user_consents",
        "care_team_assignments",
        "contact_methods",
        "user_sessions",
        "user_devices",
        "tasks",
        "call_logs",
        "support_tickets",
    ]
    for table in audit_tables:
        op.execute(f"SELECT audit_table('{table}')")


def downgrade() -> None:
    # 3. Remove Audit Triggers
    audit_tables = [
        "organizations",
        "users",
        "patients",
        "appointments",
        "documents",
        "user_consents",
        "care_team_assignments",
        "contact_methods",
        "user_sessions",
        "user_devices",
        "tasks",
        "call_logs",
        "support_tickets",
    ]
    for table in audit_tables:
        op.execute(f"DROP TRIGGER IF EXISTS audit_trigger_insert ON {table}")
        op.execute(f"DROP TRIGGER IF EXISTS audit_trigger_update ON {table}")
        op.execute(f"DROP TRIGGER IF EXISTS audit_trigger_delete ON {table}")

    # 2. Remove Policies and Disable RLS (Joined)
    op.execute(
        "DROP POLICY IF EXISTS tenant_isolation_contact_methods ON contact_methods"
    )
    op.execute("ALTER TABLE contact_methods DISABLE ROW LEVEL SECURITY")

    op.execute(
        "DROP POLICY IF EXISTS tenant_isolation_care_team_assignments ON care_team_assignments"
    )
    op.execute("ALTER TABLE care_team_assignments DISABLE ROW LEVEL SECURITY")

    # 1. Remove Policies and Disable RLS (Simple)
    # Only remove for the new tables. For original tables (patients etc), we shouldn't disable RLS
    # if we want to return to "previous state" where it was supposedly enabled.
    # But since it wasn't enabled, maybe we should?
    # Ideally downgrade should reverse upgrade.
    tables_new = [
        "appointments",
        "documents",
        "tasks",
        "call_logs",
        "support_tickets",
        "invitations",
    ]
    for table in tables_new:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    # For original tables, we might leave them as is or revert policy?
    # I'll leave them to avoid accidentally opening them up if they were supposed to be closed.
