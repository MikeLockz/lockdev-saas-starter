"""complete RLS coverage for HIPAA compliance

Revision ID: 20260114_rls_coverage
Revises:
Create Date: 2026-01-14 21:30:00.000000

This migration implements comprehensive Row-Level Security (RLS) policies
to enforce tenant isolation and satisfy HIPAA §164.308(a)(4)(ii)(B) requirements.

CRITICAL: These policies are the PRIMARY defense against cross-tenant data leakage.
Application-level filtering is NOT sufficient for HIPAA compliance.

Related Documentation:
- docs/05 - rls_policies.sql (full SQL reference)
- docs/06 - rls_tests.sql (test suite)
- docs/RLS_Implementation_Guide.md (implementation guide)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260114_rls_coverage'
down_revision = None  # Update this to the previous migration ID when integrating
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Enable Row-Level Security on all tenant-scoped tables and create policies.

    Tables protected:
    - organizations, organization_memberships, organization_patients
    - providers, staff, patients, proxies
    - care_team_assignments, contact_methods, patient_proxy_assignments
    - consents, audit_logs
    """

    # ==========================================
    # HELPER FUNCTION: Check if current user is super admin
    # ==========================================
    op.execute("""
        CREATE OR REPLACE FUNCTION is_super_admin() RETURNS BOOLEAN AS $$
        BEGIN
            RETURN EXISTS (
                SELECT 1 FROM users
                WHERE id = current_setting('app.current_user_id', true)::UUID
                  AND is_super_admin = true
                  AND deleted_at IS NULL
            );
        END;
        $$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
    """)

    # ==========================================
    # 1. ORGANIZATIONS
    # ==========================================
    op.execute("ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY organizations_isolation ON organizations
            FOR ALL
            USING (
                id = current_setting('app.current_tenant_id', true)::UUID
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 2. ORGANIZATION_MEMBERSHIPS
    # ==========================================
    op.execute("ALTER TABLE organization_memberships ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY organization_memberships_isolation ON organization_memberships
            FOR ALL
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 3. PROVIDERS
    # ==========================================
    op.execute("ALTER TABLE providers ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY providers_isolation ON providers
            FOR ALL
            USING (
                user_id IN (
                    SELECT om.user_id
                    FROM organization_memberships om
                    WHERE om.organization_id = current_setting('app.current_tenant_id', true)::UUID
                      AND om.user_id = providers.user_id
                )
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 4. STAFF
    # ==========================================
    op.execute("ALTER TABLE staff ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY staff_isolation ON staff
            FOR ALL
            USING (
                user_id IN (
                    SELECT om.user_id
                    FROM organization_memberships om
                    WHERE om.organization_id = current_setting('app.current_tenant_id', true)::UUID
                      AND om.user_id = staff.user_id
                )
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 5. PATIENTS
    # ==========================================
    op.execute("ALTER TABLE patients ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY patients_isolation ON patients
            FOR ALL
            USING (
                id IN (
                    SELECT op.patient_id
                    FROM organization_patients op
                    WHERE op.organization_id = current_setting('app.current_tenant_id', true)::UUID
                )
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 6. PROXIES
    # ==========================================
    op.execute("ALTER TABLE proxies ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY proxies_isolation ON proxies
            FOR ALL
            USING (
                id IN (
                    SELECT ppa.proxy_id
                    FROM patient_proxy_assignments ppa
                    JOIN organization_patients op ON ppa.patient_id = op.patient_id
                    WHERE op.organization_id = current_setting('app.current_tenant_id', true)::UUID
                )
                OR user_id = current_setting('app.current_user_id', true)::UUID
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 7. ORGANIZATION_PATIENTS
    # ==========================================
    op.execute("ALTER TABLE organization_patients ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY organization_patients_isolation ON organization_patients
            FOR ALL
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 8. CARE_TEAM_ASSIGNMENTS
    # ==========================================
    op.execute("ALTER TABLE care_team_assignments ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY care_team_assignments_isolation ON care_team_assignments
            FOR ALL
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 9. CONTACT_METHODS
    # ==========================================
    op.execute("ALTER TABLE contact_methods ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY contact_methods_isolation ON contact_methods
            FOR ALL
            USING (
                patient_id IN (
                    SELECT op.patient_id
                    FROM organization_patients op
                    WHERE op.organization_id = current_setting('app.current_tenant_id', true)::UUID
                )
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 10. PATIENT_PROXY_ASSIGNMENTS
    # ==========================================
    op.execute("ALTER TABLE patient_proxy_assignments ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY patient_proxy_assignments_isolation ON patient_proxy_assignments
            FOR ALL
            USING (
                patient_id IN (
                    SELECT op.patient_id
                    FROM organization_patients op
                    WHERE op.organization_id = current_setting('app.current_tenant_id', true)::UUID
                )
                OR proxy_id IN (
                    SELECT id FROM proxies WHERE user_id = current_setting('app.current_user_id', true)::UUID
                )
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 11. CONSENTS
    # ==========================================
    op.execute("ALTER TABLE consents ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY consents_isolation ON consents
            FOR ALL
            USING (
                patient_id IN (
                    SELECT op.patient_id
                    FROM organization_patients op
                    WHERE op.organization_id = current_setting('app.current_tenant_id', true)::UUID
                )
                OR is_super_admin()
            );
    """)

    # ==========================================
    # 12. AUDIT_LOGS (Special Case - Immutability)
    # ==========================================
    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;")

    # Allow all authenticated users to INSERT (needed for triggers)
    op.execute("""
        CREATE POLICY audit_logs_insert ON audit_logs
            FOR INSERT
            WITH CHECK (true);
    """)

    # Restrict SELECT to current organization only
    op.execute("""
        CREATE POLICY audit_logs_select ON audit_logs
            FOR SELECT
            USING (
                organization_id = current_setting('app.current_tenant_id', true)::UUID
                OR is_super_admin()
            );
    """)

    # Prevent UPDATE (immutable)
    op.execute("""
        CREATE POLICY audit_logs_no_update ON audit_logs
            FOR UPDATE
            USING (false);
    """)

    # Prevent DELETE (immutable)
    op.execute("""
        CREATE POLICY audit_logs_no_delete ON audit_logs
            FOR DELETE
            USING (false);
    """)


def downgrade() -> None:
    """
    Rollback RLS policies and disable Row-Level Security.

    WARNING: This removes database-level tenant isolation.
    Only run in non-production environments or during emergency rollback.
    """

    # Drop all policies
    op.execute("DROP POLICY IF EXISTS organizations_isolation ON organizations;")
    op.execute("DROP POLICY IF EXISTS organization_memberships_isolation ON organization_memberships;")
    op.execute("DROP POLICY IF EXISTS providers_isolation ON providers;")
    op.execute("DROP POLICY IF EXISTS staff_isolation ON staff;")
    op.execute("DROP POLICY IF EXISTS patients_isolation ON patients;")
    op.execute("DROP POLICY IF EXISTS proxies_isolation ON proxies;")
    op.execute("DROP POLICY IF EXISTS organization_patients_isolation ON organization_patients;")
    op.execute("DROP POLICY IF EXISTS care_team_assignments_isolation ON care_team_assignments;")
    op.execute("DROP POLICY IF EXISTS contact_methods_isolation ON contact_methods;")
    op.execute("DROP POLICY IF EXISTS patient_proxy_assignments_isolation ON patient_proxy_assignments;")
    op.execute("DROP POLICY IF EXISTS consents_isolation ON consents;")

    # Drop audit log policies
    op.execute("DROP POLICY IF EXISTS audit_logs_insert ON audit_logs;")
    op.execute("DROP POLICY IF EXISTS audit_logs_select ON audit_logs;")
    op.execute("DROP POLICY IF EXISTS audit_logs_no_update ON audit_logs;")
    op.execute("DROP POLICY IF EXISTS audit_logs_no_delete ON audit_logs;")

    # Disable RLS on all tables
    op.execute("ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE organization_memberships DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE providers DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE staff DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE patients DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE proxies DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE organization_patients DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE care_team_assignments DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE contact_methods DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE patient_proxy_assignments DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE consents DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;")

    # Drop helper function
    op.execute("DROP FUNCTION IF EXISTS is_super_admin();")
