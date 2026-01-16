# Verification Checklist: Primary Provider Constraint

Use this checklist to verify the implementation is correct before deployment.

---

## Pre-Deployment Checks

### 1. File Verification

Verify all files were created:

```bash
# Check migration exists
ls -la apps/backend/migrations/versions/20260114_add_unique_primary_provider_constraint.py

# Check script exists and is executable
ls -la apps/backend/scripts/check_primary_provider_violations.py

# Check service exists
ls -la apps/backend/src/services/care_team_service.py

# Check tests exist
ls -la apps/backend/tests/services/test_care_team_constraints.py

# Check documentation
ls -la docs/PRIMARY_PROVIDER_CONSTRAINT.md
ls -la IMPLEMENTATION_SUMMARY.md
```

**Expected**: All files should exist with recent timestamps.

---

### 2. Migration Syntax Check

Verify migration syntax is valid:

```bash
cd apps/backend

# Check migration for syntax errors
python -m py_compile migrations/versions/20260114_add_unique_primary_provider_constraint.py

# Check migration appears in alembic
uv run alembic history

# Should show: 20260114_rls_coverage -> 20260114_unique_primary
```

**Expected**: No syntax errors, migration appears in history.

---

### 3. Script Functionality Check

Test the diagnostic script works (before migration):

```bash
cd apps/backend

# Run the check script
uv run python scripts/check_primary_provider_violations.py

# Expected output (if database is empty or no violations):
# ✅ SUCCESS: No violations found
```

**Expected**: Script runs without errors, produces clear output.

---

### 4. Code Review Checklist

Review the migration file:

- [ ] `upgrade()` function cleans existing duplicates
- [ ] `upgrade()` creates the partial unique index
- [ ] `downgrade()` function drops the index
- [ ] Migration has proper revision IDs
- [ ] Comments explain the business rule

Review the service file:

- [ ] `assign_primary_provider()` demotes existing primary first
- [ ] All methods have comprehensive docstrings
- [ ] Exception handling is present
- [ ] Type hints are correct (UUID, AsyncSession)
- [ ] Commit/rollback logic is sound

Review the tests:

- [ ] Tests cover constraint violations
- [ ] Tests cover multi-provider scenarios
- [ ] Tests cover multi-tenant scenarios
- [ ] Tests verify atomicity of operations
- [ ] Fixtures are properly structured

---

## Deployment Verification

### Step 1: Development Environment

```bash
# Set environment
export DATABASE_URL="postgresql://..."  # Your dev database

# Run pre-migration check
cd apps/backend
uv run python scripts/check_primary_provider_violations.py
```

**✅ Pass Criteria**: "No violations found" or violations are acceptable

---

### Step 2: Apply Migration

```bash
# Apply the migration
uv run alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade 20260114_rls_coverage -> 20260114_unique_primary
```

**✅ Pass Criteria**: Migration completes without errors

---

### Step 3: Verify Database State

```bash
# Connect to database
psql $DATABASE_URL

# Check that index exists
\d care_team_assignments

# Should show:
# Indexes:
#     "idx_unique_primary_provider_per_patient" UNIQUE, btree (organization_id, patient_id) WHERE is_primary_provider = true
```

**✅ Pass Criteria**: Index exists with correct definition

---

### Step 4: Manual Database Test

Run these SQL commands to verify constraint works:

```sql
-- Setup test data (if not exists)
INSERT INTO organizations (id, name) VALUES
    (gen_random_uuid(), 'Test Clinic A');

-- Get the org ID
SELECT id FROM organizations WHERE name = 'Test Clinic A';

-- Create test patient (use the org_id from above)
INSERT INTO patients (id, first_name, last_name, dob) VALUES
    (gen_random_uuid(), 'Test', 'Patient', '1990-01-01');

-- Get the patient ID
SELECT id FROM patients WHERE first_name = 'Test' AND last_name = 'Patient';

-- Create two test providers (you'll need user records first if FK exists)
-- Adjust based on your actual schema

-- TEST 1: Create first primary provider - should SUCCEED ✅
INSERT INTO care_team_assignments
(organization_id, patient_id, provider_id, is_primary_provider)
VALUES
    ('<org_id>', '<patient_id>', gen_random_uuid(), TRUE);

-- TEST 2: Try to create second primary - should FAIL ❌
INSERT INTO care_team_assignments
(organization_id, patient_id, provider_id, is_primary_provider)
VALUES
    ('<org_id>', '<patient_id>', gen_random_uuid(), TRUE);

-- Expected error:
-- ERROR:  duplicate key value violates unique constraint "idx_unique_primary_provider_per_patient"

-- TEST 3: Create secondary provider - should SUCCEED ✅
INSERT INTO care_team_assignments
(organization_id, patient_id, provider_id, is_primary_provider)
VALUES
    ('<org_id>', '<patient_id>', gen_random_uuid(), FALSE);

-- Verify results
SELECT
    provider_id,
    is_primary_provider,
    assigned_at
FROM care_team_assignments
WHERE patient_id = '<patient_id>'
ORDER BY is_primary_provider DESC, assigned_at;

-- Should show:
-- 1 row with is_primary_provider = TRUE
-- 1 row with is_primary_provider = FALSE
```

**✅ Pass Criteria**:
- Test 1 succeeds
- Test 2 fails with constraint error
- Test 3 succeeds
- Query shows exactly 1 primary provider

---

### Step 5: Run Test Suite

```bash
cd apps/backend

# Run just the constraint tests
uv run pytest tests/services/test_care_team_constraints.py -v

# Expected: All tests pass
```

**✅ Pass Criteria**: All tests pass (0 failures)

---

### Step 6: Service Layer Integration Test

Create a quick integration test:

```python
# tests/integration/test_primary_provider_workflow.py
import pytest
from uuid import uuid4
from src.services.care_team_service import CareTeamService

@pytest.mark.asyncio
async def test_full_primary_provider_workflow(db_session):
    """Test complete workflow: assign, change, remove"""
    org_id = uuid4()
    patient_id = uuid4()
    provider1_id = uuid4()
    provider2_id = uuid4()

    # Step 1: Assign initial primary
    await CareTeamService.assign_primary_provider(
        db=db_session,
        organization_id=org_id,
        patient_id=patient_id,
        provider_id=provider1_id
    )

    # Verify
    primary = await CareTeamService.get_primary_provider(
        db=db_session,
        organization_id=org_id,
        patient_id=patient_id
    )
    assert primary == provider1_id

    # Step 2: Change primary provider
    await CareTeamService.assign_primary_provider(
        db=db_session,
        organization_id=org_id,
        patient_id=patient_id,
        provider_id=provider2_id
    )

    # Verify primary changed
    primary = await CareTeamService.get_primary_provider(
        db=db_session,
        organization_id=org_id,
        patient_id=patient_id
    )
    assert primary == provider2_id

    # Step 3: Add secondary provider
    specialist_id = uuid4()
    await CareTeamService.add_secondary_provider(
        db=db_session,
        organization_id=org_id,
        patient_id=patient_id,
        provider_id=specialist_id
    )

    # Verify primary unchanged
    primary = await CareTeamService.get_primary_provider(
        db=db_session,
        organization_id=org_id,
        patient_id=patient_id
    )
    assert primary == provider2_id  # Still provider2

    print("✅ Full workflow test passed!")
```

Run it:
```bash
uv run pytest tests/integration/test_primary_provider_workflow.py -v -s
```

**✅ Pass Criteria**: Workflow test passes

---

### Step 7: Check Logs and Metrics

```bash
# Check application logs for any errors
tail -f /var/log/app.log | grep -i "primary.*provider\|IntegrityError"

# Check Sentry (if configured) for any constraint violations
# Navigate to: Sentry -> Issues -> Search "idx_unique_primary_provider_per_patient"
```

**✅ Pass Criteria**: No unexpected errors in logs

---

## Staging Environment Verification

Before promoting to production, repeat steps 1-7 in staging environment.

Additional checks for staging:

### Load Testing

```bash
# Simulate concurrent primary provider assignments
# This tests for race conditions

# Create test script: tests/load/concurrent_primary_assignment.py
import asyncio
from src.services.care_team_service import CareTeamService

async def assign_primary_concurrently():
    """Test concurrent assignment doesn't create duplicates"""
    org_id = uuid4()
    patient_id = uuid4()

    # Try to assign 10 different providers as primary simultaneously
    tasks = [
        CareTeamService.assign_primary_provider(
            db=get_db(),
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=uuid4()
        )
        for _ in range(10)
    ]

    # Run concurrently
    await asyncio.gather(*tasks)

    # Verify only ONE primary exists
    primary = await CareTeamService.get_primary_provider(
        db=get_db(),
        organization_id=org_id,
        patient_id=patient_id
    )

    assert primary is not None, "Should have exactly one primary"
    print(f"✅ Concurrent test passed - primary: {primary}")

asyncio.run(assign_primary_concurrently())
```

**✅ Pass Criteria**: Test completes, exactly one primary provider exists

---

### Data Migration Validation (If Existing Data)

```sql
-- Check if any patients ended up without a primary after migration
SELECT
    p.id,
    p.first_name,
    p.last_name,
    COUNT(cta.id) FILTER (WHERE cta.is_primary_provider = TRUE) as primary_count
FROM patients p
LEFT JOIN care_team_assignments cta ON cta.patient_id = p.id
GROUP BY p.id, p.first_name, p.last_name
HAVING COUNT(cta.id) FILTER (WHERE cta.is_primary_provider = TRUE) = 0
    AND COUNT(cta.id) > 0;  -- Has care team but no primary

-- Expected: 0 rows (or acceptable number based on business rules)
```

**✅ Pass Criteria**: Acceptable number of patients without primary

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] All staging tests passed
- [ ] Code review completed
- [ ] Database backup created
- [ ] Rollback plan documented
- [ ] Deployment window scheduled (if needed)
- [ ] On-call engineer identified

### Deployment

- [ ] Run pre-migration check script
- [ ] Review and document any violations found
- [ ] Apply migration during low-traffic window
- [ ] Verify migration completed successfully
- [ ] Run post-migration verification queries
- [ ] Deploy application code with service layer
- [ ] Monitor logs for 15 minutes

### Post-Deployment (First 24 Hours)

- [ ] Monitor error rates (Sentry/logs)
- [ ] Check for constraint violation attempts
- [ ] Verify primary provider assignments working
- [ ] Review application performance metrics
- [ ] Confirm no degradation in response times

### Post-Deployment (First Week)

- [ ] Review usage patterns of service layer methods
- [ ] Identify any direct database access that needs refactoring
- [ ] Gather developer feedback on API usability
- [ ] Monitor for edge cases not covered by tests

---

## Rollback Verification (If Needed)

If you need to rollback:

```bash
# Rollback migration
cd apps/backend
uv run alembic downgrade -1

# Verify index is removed
psql $DATABASE_URL -c "\d care_team_assignments"

# Should NOT show idx_unique_primary_provider_per_patient
```

**Post-Rollback Actions**:
1. Document reason for rollback
2. Identify root cause
3. Fix issue
4. Re-test in development
5. Re-deploy when ready

---

## Sign-Off

Once all checks pass, get sign-off from:

- [ ] Backend Lead - Code quality and architecture
- [ ] DBA/DevOps - Migration safety and performance
- [ ] QA Lead - Test coverage and manual testing
- [ ] Product Owner - Business rule correctness

---

## Quick Reference Commands

```bash
# Pre-migration check
uv run python scripts/check_primary_provider_violations.py

# Apply migration
uv run alembic upgrade head

# Verify index exists
psql $DATABASE_URL -c "\d care_team_assignments" | grep idx_unique

# Run tests
uv run pytest tests/services/test_care_team_constraints.py -v

# Check for violations post-migration
psql $DATABASE_URL -c "
SELECT organization_id, patient_id, COUNT(*)
FROM care_team_assignments
WHERE is_primary_provider = TRUE
GROUP BY organization_id, patient_id
HAVING COUNT(*) > 1;
"

# Rollback (if needed)
uv run alembic downgrade -1
```

---

**Last Updated**: 2026-01-14
**Version**: 1.0
**Status**: Ready for Use
