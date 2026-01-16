-- ==========================================
-- ROW-LEVEL SECURITY (RLS) POLICIES
-- ==========================================
-- This migration implements comprehensive Row-Level Security policies
-- to enforce tenant isolation and HIPAA compliance requirements.
--
-- CRITICAL: These policies are the PRIMARY defense against cross-tenant
-- data leakage. Application-level filtering is NOT sufficient for HIPAA.
--
-- Context Variables Used:
--   app.current_tenant_id - The organization_id for the current request
--   app.current_user_id   - The user_id making the request
--
-- These variables MUST be set by the application layer at the start of
-- each database transaction using:
--   SELECT set_config('app.current_tenant_id', '<uuid>', true);
--   SELECT set_config('app.current_user_id', '<uuid>', true);
--
-- Migration Date: 2026-01-14
-- Related to: HIPAA §164.308(a)(4)(ii)(B) - Access Control
-- ==========================================

-- ==========================================
-- HELPER FUNCTION: Check if current user is super admin
-- ==========================================
-- This function is used in RLS policies to allow super admins to bypass
-- tenant isolation for administrative and support purposes.
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

-- ==========================================
-- 1. ORGANIZATIONS
-- ==========================================
-- Policy: Each organization can only see itself
-- Super admins can see all organizations
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;

CREATE POLICY organizations_isolation ON organizations
    FOR ALL
    USING (
        id = current_setting('app.current_tenant_id', true)::UUID
        OR is_super_admin()
    );

-- ==========================================
-- 2. ORGANIZATION_MEMBERSHIPS
-- ==========================================
-- Policy: Users can only see memberships for their current organization
-- Super admins can see all memberships
ALTER TABLE organization_memberships ENABLE ROW LEVEL SECURITY;

CREATE POLICY organization_memberships_isolation ON organization_memberships
    FOR ALL
    USING (
        organization_id = current_setting('app.current_tenant_id', true)::UUID
        OR is_super_admin()
    );

-- ==========================================
-- 3. PROVIDERS
-- ==========================================
-- Policy: Providers are accessible if the current user is a member of
-- any organization where this provider is also a member
-- Super admins can see all providers
ALTER TABLE providers ENABLE ROW LEVEL SECURITY;

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

-- ==========================================
-- 4. STAFF
-- ==========================================
-- Policy: Staff are accessible if the current user is a member of
-- any organization where this staff member is also a member
-- Super admins can see all staff
ALTER TABLE staff ENABLE ROW LEVEL SECURITY;

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

-- ==========================================
-- 5. PATIENTS
-- ==========================================
-- Policy: Patients are accessible only if they belong to the current organization
-- This is enforced via the organization_patients join table
-- Super admins can see all patients
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;

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

-- ==========================================
-- 6. PROXIES
-- ==========================================
-- Policy: Proxies are accessible if they manage patients in the current organization
-- OR if the proxy is the current user (self-access)
-- Super admins can see all proxies
ALTER TABLE proxies ENABLE ROW LEVEL SECURITY;

CREATE POLICY proxies_isolation ON proxies
    FOR ALL
    USING (
        -- Proxy manages patients in this org
        id IN (
            SELECT ppa.proxy_id
            FROM patient_proxy_assignments ppa
            JOIN organization_patients op ON ppa.patient_id = op.patient_id
            WHERE op.organization_id = current_setting('app.current_tenant_id', true)::UUID
        )
        -- OR proxy is the current user (self-access)
        OR user_id = current_setting('app.current_user_id', true)::UUID
        OR is_super_admin()
    );

-- ==========================================
-- 7. ORGANIZATION_PATIENTS (Join Table)
-- ==========================================
-- Policy: Direct organization_id check
-- Super admins can see all relationships
ALTER TABLE organization_patients ENABLE ROW LEVEL SECURITY;

CREATE POLICY organization_patients_isolation ON organization_patients
    FOR ALL
    USING (
        organization_id = current_setting('app.current_tenant_id', true)::UUID
        OR is_super_admin()
    );

-- ==========================================
-- 8. CARE_TEAM_ASSIGNMENTS
-- ==========================================
-- Policy: Care team assignments are only visible within their organization
-- Super admins can see all assignments
ALTER TABLE care_team_assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY care_team_assignments_isolation ON care_team_assignments
    FOR ALL
    USING (
        organization_id = current_setting('app.current_tenant_id', true)::UUID
        OR is_super_admin()
    );

-- ==========================================
-- 9. CONTACT_METHODS
-- ==========================================
-- Policy: Contact methods are accessible if their patient belongs to current org
-- Super admins can see all contact methods
ALTER TABLE contact_methods ENABLE ROW LEVEL SECURITY;

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

-- ==========================================
-- 10. PATIENT_PROXY_ASSIGNMENTS
-- ==========================================
-- Policy: Proxy assignments are visible if the patient belongs to current org
-- OR if the current user is the proxy (self-access)
-- Super admins can see all assignments
ALTER TABLE patient_proxy_assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY patient_proxy_assignments_isolation ON patient_proxy_assignments
    FOR ALL
    USING (
        patient_id IN (
            SELECT op.patient_id
            FROM organization_patients op
            WHERE op.organization_id = current_setting('app.current_tenant_id', true)::UUID
        )
        -- OR current user is the proxy (self-access)
        OR proxy_id IN (
            SELECT id FROM proxies WHERE user_id = current_setting('app.current_user_id', true)::UUID
        )
        OR is_super_admin()
    );

-- ==========================================
-- 11. CONSENTS
-- ==========================================
-- Policy: Consents are visible if their patient belongs to current org
-- Super admins can see all consents
ALTER TABLE consents ENABLE ROW LEVEL SECURITY;

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

-- ==========================================
-- 12. AUDIT_LOGS
-- ==========================================
-- Policy: Audit logs are scoped by organization
-- Special rule: Allow INSERT by all authenticated users (for triggers)
-- SELECT is restricted to current organization only
-- Super admins can see all audit logs
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Allow all authenticated users to INSERT audit logs (needed for triggers)
CREATE POLICY audit_logs_insert ON audit_logs
    FOR INSERT
    WITH CHECK (true);

-- Restrict SELECT to current organization only
CREATE POLICY audit_logs_select ON audit_logs
    FOR SELECT
    USING (
        organization_id = current_setting('app.current_tenant_id', true)::UUID
        OR is_super_admin()
    );

-- Prevent UPDATE and DELETE of audit logs (immutable)
CREATE POLICY audit_logs_no_update ON audit_logs
    FOR UPDATE
    USING (false);

CREATE POLICY audit_logs_no_delete ON audit_logs
    FOR DELETE
    USING (false);

-- ==========================================
-- 13. USERS TABLE
-- ==========================================
-- Note: Users table does NOT have RLS enabled because:
-- 1. Users are global entities that can belong to multiple organizations
-- 2. User access is controlled via organization_memberships RLS
-- 3. Application layer must filter user queries appropriately
--
-- If strict user isolation is required, uncomment the policy below:
--
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY users_isolation ON users
--     FOR ALL
--     USING (
--         -- User is a member of current org
--         id IN (
--             SELECT om.user_id
--             FROM organization_memberships om
--             WHERE om.organization_id = current_setting('app.current_tenant_id', true)::UUID
--         )
--         -- OR user is the current user (self-access)
--         OR id = current_setting('app.current_user_id', true)::UUID
--         OR is_super_admin()
--     );

-- ==========================================
-- VERIFICATION QUERIES
-- ==========================================
-- Run these queries to verify RLS is enabled on all tables:
--
-- SELECT tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY tablename;
--
-- View all policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;

-- ==========================================
-- ROLLBACK SCRIPT
-- ==========================================
-- To rollback this migration, run:
--
-- DROP POLICY IF EXISTS organizations_isolation ON organizations;
-- DROP POLICY IF EXISTS organization_memberships_isolation ON organization_memberships;
-- DROP POLICY IF EXISTS providers_isolation ON providers;
-- DROP POLICY IF EXISTS staff_isolation ON staff;
-- DROP POLICY IF EXISTS patients_isolation ON patients;
-- DROP POLICY IF EXISTS proxies_isolation ON proxies;
-- DROP POLICY IF EXISTS organization_patients_isolation ON organization_patients;
-- DROP POLICY IF EXISTS care_team_assignments_isolation ON care_team_assignments;
-- DROP POLICY IF EXISTS contact_methods_isolation ON contact_methods;
-- DROP POLICY IF EXISTS patient_proxy_assignments_isolation ON patient_proxy_assignments;
-- DROP POLICY IF EXISTS consents_isolation ON consents;
-- DROP POLICY IF EXISTS audit_logs_insert ON audit_logs;
-- DROP POLICY IF EXISTS audit_logs_select ON audit_logs;
-- DROP POLICY IF EXISTS audit_logs_no_update ON audit_logs;
-- DROP POLICY IF EXISTS audit_logs_no_delete ON audit_logs;
--
-- ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE organization_memberships DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE providers DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE staff DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE patients DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE proxies DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE organization_patients DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE care_team_assignments DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE contact_methods DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE patient_proxy_assignments DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE consents DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;
--
-- DROP FUNCTION IF EXISTS is_super_admin();
