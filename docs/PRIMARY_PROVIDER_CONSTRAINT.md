# Primary Provider Constraint Documentation

## Overview

This document explains the "One Primary Provider" database constraint and how to work with it.

**Business Rule**: Each patient can have only ONE provider marked as "primary" within a given organization at any time.

**Implementation**: PostgreSQL partial unique index on `care_team_assignments` table

**Migration**: `20260114_add_unique_primary_provider_constraint.py`

---

## Why This Constraint Exists

### Clinical Accountability
- The primary provider is the main point of accountability for patient care
- Clear designation prevents confusion about who is responsible for care coordination
- Required for proper care team workflows and handoffs

### Data Integrity
- Prevents application bugs from creating ambiguous states
- Enforces business rules at the database level (defense in depth)
- Ensures consistent data regardless of application layer changes

### Compliance
- HIPAA requires clear accountability for patient data access
- Audit trails need to identify the primary responsible clinician
- Care coordination documentation requires explicit primary designation

---

## Technical Implementation

### Database Constraint

```sql
CREATE UNIQUE INDEX idx_unique_primary_provider_per_patient
ON care_team_assignments (organization_id, patient_id)
WHERE is_primary_provider = TRUE;
```

**How It Works:**
- **Partial Index**: Only indexes rows where `is_primary_provider = TRUE`
- **Composite Key**: Uniqueness enforced on `(organization_id, patient_id)` pair
- **Minimal Overhead**: Does NOT index secondary providers (is_primary = FALSE)

**What It Allows:**
✅ Multiple providers with `is_primary_provider = FALSE` (secondary/consulting)
✅ Same provider can be primary for different patients
✅ Same patient can have different primaries at different organizations

**What It Prevents:**
❌ Two providers both marked as primary for same patient in same org

---

## How to Use in Application Code

### ✅ CORRECT: Use the Service Layer

```python
from src.services.care_team_service import CareTeamService

# Assign a new primary provider (automatically demotes existing primary)
await CareTeamService.assign_primary_provider(
    db=session,
    organization_id=clinic_id,
    patient_id=patient.id,
    provider_id=new_doctor.id
)

# Add a secondary/consulting provider
await CareTeamService.add_secondary_provider(
    db=session,
    organization_id=clinic_id,
    patient_id=patient.id,
    provider_id=specialist.id
)

# Get the current primary provider
primary_id = await CareTeamService.get_primary_provider(
    db=session,
    organization_id=clinic_id,
    patient_id=patient.id
)
```

### ❌ INCORRECT: Direct Database Manipulation

```python
# DON'T DO THIS - Will cause constraint violation!
assignment = CareTeamAssignment(
    organization_id=org_id,
    patient_id=patient_id,
    provider_id=provider2_id,
    is_primary_provider=True  # If another primary exists, this will FAIL
)
db.add(assignment)
await db.commit()  # ❌ IntegrityError!
```

### ✅ CORRECT: Safe Direct Access Pattern

If you must work directly with the model (not recommended):

```python
# STEP 1: Demote existing primary (if any)
await db.execute(
    update(CareTeamAssignment)
    .where(
        CareTeamAssignment.organization_id == org_id,
        CareTeamAssignment.patient_id == patient_id,
        CareTeamAssignment.is_primary_provider == True
    )
    .values(is_primary_provider=False)
)

# STEP 2: Promote new primary
new_assignment.is_primary_provider = True
await db.commit()  # ✅ Safe - only one primary exists
```

---

## Migration Instructions

### Pre-Migration Check

Before applying the migration, check for existing violations:

```bash
cd apps/backend
uv run python scripts/check_primary_provider_violations.py
```

**If violations are found:**
1. The script will show which patients have multiple primaries
2. The migration will automatically keep the EARLIEST assigned provider
3. All other primaries will be demoted to secondary

**To manually resolve** (if automatic resolution is not correct):

```sql
-- Set the CORRECT provider as primary
UPDATE care_team_assignments
SET is_primary_provider = TRUE
WHERE id = '<correct_assignment_id>';

-- Clear all other primaries for this patient
UPDATE care_team_assignments
SET is_primary_provider = FALSE
WHERE organization_id = '<org_id>'
  AND patient_id = '<patient_id>'
  AND id != '<correct_assignment_id>';
```

### Apply Migration

```bash
# Create the migration (if not already created)
make migrate-create name="add_unique_primary_provider_constraint"

# Apply the migration
make migrate

# Verify it was applied
psql $DATABASE_URL -c "\d care_team_assignments"
# Should show: idx_unique_primary_provider_per_patient
```

### Rollback (if needed)

```bash
# Downgrade to previous version
cd apps/backend
uv run alembic downgrade -1

# This will remove the unique index
# WARNING: Data integrity is no longer enforced!
```

---

## Testing

### Run Automated Tests

```bash
# Run all constraint tests
cd apps/backend
uv run pytest tests/services/test_care_team_constraints.py -v

# Run specific test
uv run pytest tests/services/test_care_team_constraints.py::TestPrimaryProviderConstraint::test_one_primary_provider_per_patient -v
```

### Manual Database Test

```sql
-- Setup test data
INSERT INTO organizations (id, name) VALUES ('org1', 'Test Clinic');
INSERT INTO patients (id, first_name, last_name, dob)
VALUES ('patient1', 'John', 'Doe', '1990-01-01');
INSERT INTO providers (id, user_id, npi_number)
VALUES ('provider1', 'user1', '1234567890'),
       ('provider2', 'user2', '0987654321');

-- Test 1: Create first primary - should SUCCEED ✅
INSERT INTO care_team_assignments
(organization_id, patient_id, provider_id, is_primary_provider)
VALUES ('org1', 'patient1', 'provider1', TRUE);

-- Test 2: Create second primary - should FAIL ❌
INSERT INTO care_team_assignments
(organization_id, patient_id, provider_id, is_primary_provider)
VALUES ('org1', 'patient1', 'provider2', TRUE);
-- Expected: ERROR - duplicate key value violates unique constraint "idx_unique_primary_provider_per_patient"

-- Test 3: Create secondary provider - should SUCCEED ✅
INSERT INTO care_team_assignments
(organization_id, patient_id, provider_id, is_primary_provider)
VALUES ('org1', 'patient1', 'provider2', FALSE);

-- Test 4: Promote secondary to primary (safe way) - should SUCCEED ✅
BEGIN;
  -- Demote current primary
  UPDATE care_team_assignments
  SET is_primary_provider = FALSE
  WHERE organization_id = 'org1' AND patient_id = 'patient1'
    AND provider_id = 'provider1';

  -- Promote new primary
  UPDATE care_team_assignments
  SET is_primary_provider = TRUE
  WHERE organization_id = 'org1' AND patient_id = 'patient1'
    AND provider_id = 'provider2';
COMMIT;
```

---

## Common Scenarios

### Scenario 1: Changing Primary Provider

**Use Case**: Patient switches from Dr. Smith to Dr. Jones

```python
# Option A: Use service (RECOMMENDED)
await CareTeamService.assign_primary_provider(
    db=session,
    organization_id=clinic_id,
    patient_id=patient.id,
    provider_id=dr_jones_id  # Automatically demotes Dr. Smith
)

# Option B: Manual (if needed)
async with db.begin():
    # Demote Dr. Smith
    await db.execute(
        update(CareTeamAssignment)
        .where(
            CareTeamAssignment.organization_id == clinic_id,
            CareTeamAssignment.patient_id == patient.id,
            CareTeamAssignment.provider_id == dr_smith_id
        )
        .values(is_primary_provider=False)
    )

    # Promote Dr. Jones
    await db.execute(
        update(CareTeamAssignment)
        .where(
            CareTeamAssignment.organization_id == clinic_id,
            CareTeamAssignment.patient_id == patient.id,
            CareTeamAssignment.provider_id == dr_jones_id
        )
        .values(is_primary_provider=True)
    )
```

### Scenario 2: Adding Specialist Consultants

**Use Case**: Patient's primary is Dr. Smith, needs cardiology consult from Dr. Lee

```python
# Primary remains Dr. Smith, add Dr. Lee as secondary
await CareTeamService.add_secondary_provider(
    db=session,
    organization_id=clinic_id,
    patient_id=patient.id,
    provider_id=dr_lee_id  # Added as secondary (is_primary=FALSE)
)

# Result: Dr. Smith = primary, Dr. Lee = secondary consultant
```

### Scenario 3: Provider Leaves Practice

**Use Case**: Dr. Smith leaves, need to reassign patients to Dr. Jones

```python
# Get all patients where Dr. Smith is primary
patients = await db.execute(
    select(CareTeamAssignment)
    .where(
        CareTeamAssignment.organization_id == clinic_id,
        CareTeamAssignment.provider_id == dr_smith_id,
        CareTeamAssignment.is_primary_provider == True
    )
)

# Reassign each patient to Dr. Jones
for assignment in patients.scalars():
    await CareTeamService.assign_primary_provider(
        db=session,
        organization_id=clinic_id,
        patient_id=assignment.patient_id,
        provider_id=dr_jones_id
    )

    # Optionally remove Dr. Smith from care team
    await CareTeamService.remove_from_care_team(
        db=session,
        organization_id=clinic_id,
        patient_id=assignment.patient_id,
        provider_id=dr_smith_id
    )
```

### Scenario 4: Multi-Clinic Patient

**Use Case**: Patient sees Dr. Smith at Clinic A, Dr. Jones at Clinic B

```python
# This is ALLOWED - different organizations
await CareTeamService.assign_primary_provider(
    db=session,
    organization_id=clinic_a_id,  # Different org
    patient_id=patient.id,
    provider_id=dr_smith_id
)

await CareTeamService.assign_primary_provider(
    db=session,
    organization_id=clinic_b_id,  # Different org
    patient_id=patient.id,
    provider_id=dr_jones_id  # ✅ Allowed - different organization
)
```

---

## Troubleshooting

### Error: `duplicate key value violates unique constraint "idx_unique_primary_provider_per_patient"`

**Cause**: Attempted to create a second primary provider for the same patient in the same organization.

**Solution**:
1. Use `CareTeamService.assign_primary_provider()` which handles demotion automatically
2. Or manually demote the existing primary before creating a new one

### Query to Find Current Primary

```sql
SELECT provider_id
FROM care_team_assignments
WHERE organization_id = '<org_id>'
  AND patient_id = '<patient_id>'
  AND is_primary_provider = TRUE;
```

### Query to Find All Violations (Post-Migration)

```sql
-- Should return 0 rows if constraint is working
SELECT organization_id, patient_id, COUNT(*) as primary_count
FROM care_team_assignments
WHERE is_primary_provider = TRUE
GROUP BY organization_id, patient_id
HAVING COUNT(*) > 1;
```

---

## Related Files

- **Migration**: `apps/backend/migrations/versions/20260114_add_unique_primary_provider_constraint.py`
- **Service**: `apps/backend/src/services/care_team_service.py`
- **Tests**: `apps/backend/tests/services/test_care_team_constraints.py`
- **Check Script**: `apps/backend/scripts/check_primary_provider_violations.py`
- **Schema**: `docs/04 - sql.ddl` (line 123-142)

---

## FAQ

**Q: Can a patient have multiple providers on their care team?**
A: Yes! A patient can have unlimited providers. Only ONE can be marked as "primary".

**Q: Can the same provider be primary for multiple patients?**
A: Yes! A provider can be the primary for as many patients as needed.

**Q: What happens to secondary providers when I change the primary?**
A: Nothing. Secondary providers remain unchanged. Only the `is_primary_provider` flag changes.

**Q: Can I have NO primary provider for a patient?**
A: Yes. The constraint only prevents MULTIPLE primaries, not zero primaries.

**Q: Does this work with soft-deletes?**
A: Yes. Deleted assignments (if you implement soft deletes) should be excluded from the care team queries.

**Q: What about multi-tenancy/RLS?**
A: The constraint is compatible with RLS. The `organization_id` in the index ensures tenant isolation.

---

## Support

For questions or issues:
1. Check the test suite: `test_care_team_constraints.py`
2. Review the service implementation: `care_team_service.py`
3. Run the violation check script before debugging
4. Check database logs for constraint violation details

---

*Last Updated: 2026-01-14*
*Migration Version: 20260114_unique_primary*
