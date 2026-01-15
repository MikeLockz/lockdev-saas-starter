"""audit_and_rls

Revision ID: f47bf61a922e
Revises: 5059b27c2936
Create Date: 2025-12-31 11:37:15.477660

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f47bf61a922e"
down_revision: str | Sequence[str] | None = "5059b27c2936"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create Audit Trigger Function
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_trigger_func()
    RETURNS TRIGGER AS $$
    DECLARE
        v_user_id UUID;
        v_org_id UUID;
        v_changes JSONB;
        v_action VARCHAR;
    BEGIN
        -- Attempt to get context variables
        BEGIN
            v_user_id := current_setting('app.current_user_id', true)::UUID;
            v_org_id := current_setting('app.current_tenant_id', true)::UUID;
        EXCEPTION WHEN OTHERS THEN
            v_user_id := NULL;
            v_org_id := NULL;
        END;

        v_action := TG_OP;

        IF (TG_OP = 'DELETE') THEN
            v_changes := row_to_json(OLD)::JSONB;
        ELSIF (TG_OP = 'INSERT') THEN
            v_changes := row_to_json(NEW)::JSONB;
        ELSIF (TG_OP = 'UPDATE') THEN
            v_changes := row_to_json(NEW)::JSONB;
        END IF;

        INSERT INTO audit_logs (
            actor_user_id,
            organization_id,
            resource_type,
            resource_id,
            action_type,
            changes_json,
            occurred_at
        ) VALUES (
            v_user_id,
            v_org_id,
            TG_TABLE_NAME,
            CASE
                WHEN TG_OP = 'DELETE' THEN OLD.id
                ELSE NEW.id
            END,
            v_action,
            v_changes,
            NOW()
        );

        RETURN NULL; -- result is ignored since this is an AFTER trigger
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # 2. Attach Triggers
    tables = ["patients", "organization_memberships", "proxies", "consent_documents", "user_consents"]

    for table in tables:
        op.execute(f"""
        CREATE TRIGGER audit_trigger_{table}
        AFTER INSERT OR UPDATE OR DELETE ON {table}
        FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
        """)

    # 3. Enable RLS
    rls_tables = ["patients", "proxies", "organization_memberships", "audit_logs"]

    for table in rls_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

    # 4. Create Policies

    # Audit Logs: Insert by all (required for triggers/system), Select by tenant
    op.execute("""
    CREATE POLICY audit_logs_insert ON audit_logs FOR INSERT WITH CHECK (true)
    """)

    op.execute("""
    CREATE POLICY audit_logs_select ON audit_logs FOR SELECT USING (
        organization_id = current_setting('app.current_tenant_id', true)::UUID
        OR
        actor_user_id = current_setting('app.current_user_id', true)::UUID
    )
    """)

    # Organization Memberships: Visible by organization
    op.execute("""
    CREATE POLICY org_members_isolation ON organization_memberships
    USING (organization_id = current_setting('app.current_tenant_id', true)::UUID);
    """)

    # Patients: M:N via organization_patients
    # Note: RLS policies can be expensive if subqueries are complex.
    # Ensuring organization_patients has indexes (it does, PK).
    op.execute("""
    CREATE POLICY patient_isolation ON patients
    USING (
        id IN (
            SELECT patient_id 
            FROM organization_patients 
            WHERE organization_id = current_setting('app.current_tenant_id', true)::UUID
        )
    );
    """)

    # Proxies: Direct via user_id? No, proxies link to users, but conceptual ownership?
    # Proxies are linked to patients via patient_proxy_assignments.
    # This acts as a secondary check. For now, let's limit visibility to the user themselves
    # OR if they are a proxy for a patient in the current org.
    # Simple first pass: Only view your own proxy record if you are that user.
    op.execute("""
    CREATE POLICY proxy_user_isolation ON proxies
    USING (user_id = current_setting('app.current_user_id', true)::UUID);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop Policies
    op.execute("DROP POLICY IF EXISTS proxy_user_isolation ON proxies")
    op.execute("DROP POLICY IF EXISTS patient_isolation ON patients")
    op.execute("DROP POLICY IF EXISTS org_members_isolation ON organization_memberships")
    op.execute("DROP POLICY IF EXISTS audit_logs_select ON audit_logs")
    op.execute("DROP POLICY IF EXISTS audit_logs_insert ON audit_logs")

    # Disable RLS
    rls_tables = ["patients", "proxies", "organization_memberships", "audit_logs"]
    for table in rls_tables:
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    # Drop Triggers
    tables = ["patients", "organization_memberships", "proxies", "consent_documents", "user_consents"]
    for table in tables:
        op.execute(f"DROP TRIGGER IF EXISTS audit_trigger_{table} ON {table}")

    # Drop Function
    op.execute("DROP FUNCTION IF EXISTS audit_trigger_func")
