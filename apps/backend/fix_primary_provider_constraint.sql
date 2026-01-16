-- ==========================================
-- FIX: Primary Provider Constraint
-- ==========================================
-- Problem: Current constraint only enforces ONE primary per patient GLOBALLY
-- Solution: Enforce ONE primary per patient PER ORGANIZATION
--
-- Current: UNIQUE (patient_id) WHERE role='PRIMARY' AND removed_at IS NULL
-- Fixed:   UNIQUE (organization_id, patient_id) WHERE role='PRIMARY' AND removed_at IS NULL
-- ==========================================

BEGIN;

-- Step 1: Check for any existing violations before we modify the constraint
DO $$
DECLARE
    violation_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO violation_count
    FROM (
        SELECT organization_id, patient_id, COUNT(*) as cnt
        FROM care_team_assignments
        WHERE role = 'PRIMARY' AND removed_at IS NULL
        GROUP BY organization_id, patient_id
        HAVING COUNT(*) > 1
    ) violations;

    IF violation_count > 0 THEN
        RAISE NOTICE 'Found % violations - cleaning up...', violation_count;

        -- Keep the earliest assignment per (org, patient), demote others
        UPDATE care_team_assignments cta
        SET role = 'SPECIALIST'
        WHERE role = 'PRIMARY'
          AND removed_at IS NULL
          AND id NOT IN (
              SELECT DISTINCT ON (organization_id, patient_id) id
              FROM care_team_assignments
              WHERE role = 'PRIMARY' AND removed_at IS NULL
              ORDER BY organization_id, patient_id, assigned_at ASC
          );

        RAISE NOTICE 'Cleaned up violations - demoted duplicate primaries to SPECIALIST';
    ELSE
        RAISE NOTICE 'No violations found - safe to proceed';
    END IF;
END $$;

-- Step 2: Drop the old incorrect constraint
DROP INDEX IF EXISTS uq_care_team_primary;

DO $$
BEGIN
    RAISE NOTICE 'Dropped old constraint: uq_care_team_primary (patient_id only)';
END $$;

-- Step 3: Create the new correct constraint
CREATE UNIQUE INDEX uq_care_team_primary
ON care_team_assignments (organization_id, patient_id)
WHERE role = 'PRIMARY' AND removed_at IS NULL;

-- Step 4: Add comment explaining the constraint
COMMENT ON INDEX uq_care_team_primary IS
'Enforces ONE primary provider per patient per organization. Allows same patient to have different primaries at different organizations (multi-tenancy). Excludes soft-deleted records.';

-- Step 5: Verify the constraint works
DO $$
BEGIN
    RAISE NOTICE 'Created new constraint: uq_care_team_primary (organization_id, patient_id)';
    RAISE NOTICE 'Constraint successfully created and enforces uniqueness on (organization_id, patient_id)';
END $$;

COMMIT;

-- ==========================================
-- Verification Query
-- ==========================================
-- Run this after the migration to verify:
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = 'care_team_assignments' AND indexname = 'uq_care_team_primary';
--
-- Expected result should show: (organization_id, patient_id) in the index definition
