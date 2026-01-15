-- Pre-migration validation script to check for existing PRIMARY provider violations
--
-- This script checks if there are any patients with multiple PRIMARY providers
-- before applying the unique constraint migration n8o9p0q1r2s3.
--
-- Usage:
--   psql -d <your_database> -f check_primary_violations.sql
--   OR run this query in your database client

\echo '======================================================================'
\echo 'PRIMARY Provider Constraint - Pre-Migration Validation'
\echo '======================================================================'
\echo ''

-- Check for violations
WITH violations AS (
    SELECT
        patient_id,
        COUNT(*) as primary_count,
        array_agg(provider_id) as provider_ids,
        array_agg(id) as assignment_ids
    FROM care_team_assignments
    WHERE role = 'PRIMARY' AND removed_at IS NULL
    GROUP BY patient_id
    HAVING COUNT(*) > 1
    ORDER BY primary_count DESC
)
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ No violations found! Safe to apply migration n8o9p0q1r2s3'
        ELSE '❌ Found ' || COUNT(*) || ' patient(s) with multiple PRIMARY providers - MANUAL RESOLUTION REQUIRED'
    END as status
FROM violations;

-- Show detailed violation information
\echo ''
\echo 'Detailed Violation Report:'
\echo '======================================================================'

SELECT
    patient_id,
    COUNT(*) as primary_count,
    array_agg(provider_id::text) as provider_ids,
    array_agg(id::text) as assignment_ids
FROM care_team_assignments
WHERE role = 'PRIMARY' AND removed_at IS NULL
GROUP BY patient_id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;

\echo ''
\echo 'If violations were found, resolve them using one of these approaches:'
\echo ''
\echo 'Option 1 - Change role to SPECIALIST:'
\echo '  UPDATE care_team_assignments'
\echo '  SET role = ''SPECIALIST'''
\echo '  WHERE id = ''<assignment_id_to_demote>'';'
\echo ''
\echo 'Option 2 - Soft delete the assignment:'
\echo '  UPDATE care_team_assignments'
\echo '  SET removed_at = NOW()'
\echo '  WHERE id = ''<assignment_id_to_remove>'';'
\echo ''
\echo 'After resolving, run this script again to verify.'
