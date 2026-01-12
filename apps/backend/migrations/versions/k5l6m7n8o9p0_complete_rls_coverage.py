"""complete_rls_coverage

Revision ID: k5l6m7n8o9p0
Revises: j4k5l6m7n8o9
Create Date: 2026-01-11 21:30:00.000000

Adds Row-Level Security (RLS) policies to all remaining PHI tables for defense-in-depth.
This addresses P1-004 and P1-005 from the security audit.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "k5l6m7n8o9p0"
down_revision: str | Sequence[str] | None = "j4k5l6m7n8o9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enable RLS and create policies for remaining PHI tables."""

    # Tables that need RLS but don't have it yet
    tables_to_protect = [
        "appointments",
        "documents",
        "care_team_assignments",
        "contact_methods",
        "consent_documents",
        "user_consents",
        "providers",
        "staff",
        "user_sessions",
    ]

    # Enable RLS on all tables
    for table in tables_to_protect:
        op.execute(f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = '{table}'
            ) THEN
                ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
            END IF;
        END $$;
        """)

    # Appointments: Scoped by organization_id
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'appointments'
        ) THEN
            -- Drop policy if it exists (for idempotency)
            DROP POLICY IF EXISTS appointment_isolation ON appointments;

            CREATE POLICY appointment_isolation ON appointments
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
            );
        END IF;
    END $$;
    """)

    # Documents: Scoped by organization_id
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'documents'
        ) THEN
            DROP POLICY IF EXISTS document_isolation ON documents;

            CREATE POLICY document_isolation ON documents
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
            );
        END IF;
    END $$;
    """)

    # Care Team Assignments: Scoped by organization_id
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'care_team_assignments'
        ) THEN
            DROP POLICY IF EXISTS care_team_isolation ON care_team_assignments;

            CREATE POLICY care_team_isolation ON care_team_assignments
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
            );
        END IF;
    END $$;
    """)

    # Contact Methods: Via patient relationship
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'contact_methods'
        ) THEN
            DROP POLICY IF EXISTS contact_method_isolation ON contact_methods;

            CREATE POLICY contact_method_isolation ON contact_methods
            USING (
                patient_id IN (
                    SELECT patient_id
                    FROM organization_patients
                    WHERE organization_id = current_setting('app.current_tenant_id', true)::UUID
                )
            );
        END IF;
    END $$;
    """)

    # Consent Documents: Via patient relationship
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'consent_documents'
        ) THEN
            DROP POLICY IF EXISTS consent_document_isolation ON consent_documents;

            CREATE POLICY consent_document_isolation ON consent_documents
            USING (
                patient_id IN (
                    SELECT patient_id
                    FROM organization_patients
                    WHERE organization_id = current_setting('app.current_tenant_id', true)::UUID
                )
            );
        END IF;
    END $$;
    """)

    # User Consents: Via patient relationship
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'user_consents'
        ) THEN
            DROP POLICY IF EXISTS user_consent_isolation ON user_consents;

            CREATE POLICY user_consent_isolation ON user_consents
            USING (
                patient_id IN (
                    SELECT patient_id
                    FROM organization_patients
                    WHERE organization_id = current_setting('app.current_tenant_id', true)::UUID
                )
            );
        END IF;
    END $$;
    """)

    # Providers: Scoped by organization_id
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'providers'
        ) THEN
            DROP POLICY IF EXISTS provider_isolation ON providers;

            CREATE POLICY provider_isolation ON providers
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
            );
        END IF;
    END $$;
    """)

    # Staff: Scoped by organization_id
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'staff'
        ) THEN
            DROP POLICY IF EXISTS staff_isolation ON staff;

            CREATE POLICY staff_isolation ON staff
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
            );
        END IF;
    END $$;
    """)

    # User Sessions: Scoped by user_id (not tenant-specific)
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'user_sessions'
        ) THEN
            DROP POLICY IF EXISTS user_session_isolation ON user_sessions;

            CREATE POLICY user_session_isolation ON user_sessions
            USING (
                user_id = current_setting('app.current_user_id', true)::UUID
            );
        END IF;
    END $$;
    """)


def downgrade() -> None:
    """Remove RLS policies from tables."""

    # Drop all policies
    policies = [
        ("appointments", "appointment_isolation"),
        ("documents", "document_isolation"),
        ("care_team_assignments", "care_team_isolation"),
        ("contact_methods", "contact_method_isolation"),
        ("consent_documents", "consent_document_isolation"),
        ("user_consents", "user_consent_isolation"),
        ("providers", "provider_isolation"),
        ("staff", "staff_isolation"),
        ("user_sessions", "user_session_isolation"),
    ]

    for table, policy in policies:
        op.execute(f"DROP POLICY IF EXISTS {policy} ON {table};")

    # Disable RLS (optional - comment out if you want to keep RLS enabled)
    tables = [
        "appointments",
        "documents",
        "care_team_assignments",
        "contact_methods",
        "consent_documents",
        "user_consents",
        "providers",
        "staff",
        "user_sessions",
    ]

    for table in tables:
        op.execute(f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = '{table}'
            ) THEN
                ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;
            END IF;
        END $$;
        """)
