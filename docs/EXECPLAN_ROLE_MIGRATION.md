# Migrate Service Layer from is_primary_provider to role='PRIMARY'

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document must be maintained in accordance with PLANS.md located at `docs/plan.md`.

## Purpose / Big Picture

The database schema for care team assignments uses a `role` column with values like 'PRIMARY', 'SPECIALIST', and 'CONSULTANT'. However, the service layer code in `apps/backend/src/services/care_team_service.py` was initially written using a boolean `is_primary_provider` column that doesn't exist in the actual database schema. This creates a mismatch between the code and the database.

After completing this plan, the service layer and test suite will correctly query and update the `role` column using the value 'PRIMARY' to designate primary providers. All existing functionality will work identically, but the code will match the actual database schema. You can verify success by running the test suite and observing that all care team assignment operations correctly read and write the `role` column.

## Progress

- [ ] Read and understand current service layer implementation
- [ ] Read and understand current test suite
- [ ] Create CareTeamRole enum for type safety
- [ ] Update service layer to use role='PRIMARY' instead of is_primary_provider=True
- [ ] Update test suite to use role='PRIMARY'
- [ ] Update documentation to reflect role-based approach
- [ ] Run tests to verify changes
- [ ] Manual verification with database queries

## Surprises & Discoveries

(To be filled in during implementation)

## Decision Log

(To be filled in during implementation)

## Outcomes & Retrospective

(To be filled in at completion)

## Context and Orientation

This repository is a SaaS starter for healthcare applications with multi-tenancy support. The backend is located at `apps/backend/` and uses:
- **Python** with FastAPI for the web framework
- **SQLAlchemy** (async) for database ORM
- **PostgreSQL** as the database with Row-Level Security (RLS) for tenant isolation
- **Alembic** for database migrations
- **pytest** for testing

The care team assignment system tracks which providers are assigned to which patients within an organization. Each assignment has a `role` that can be 'PRIMARY' (the main accountable provider), 'SPECIALIST', 'CONSULTANT', or other values. The database enforces a unique constraint: only ONE provider can have role='PRIMARY' for a given (organization_id, patient_id) pair.

### Key Files

- **Service Layer**: `apps/backend/src/services/care_team_service.py` - Contains business logic for care team operations
- **Test Suite**: `apps/backend/tests/services/test_care_team_constraints.py` - Tests for constraint enforcement
- **Database Schema**: `docs/04 - sql.ddl` - Line 124-142 defines the care_team_assignments table
- **Migration**: `apps/backend/migrations/versions/20260114_add_unique_primary_provider_constraint.py` - Created the unique index
- **Database Constraint**: The unique index `uq_care_team_primary` enforces uniqueness on (organization_id, patient_id) WHERE role='PRIMARY' AND removed_at IS NULL

### Current Problem

The service layer code references a column `is_primary_provider` (boolean) that doesn't exist. The actual database has a `role` column (VARCHAR). The database constraint created in migration 20260114 uses `WHERE role = 'PRIMARY'`, but the service code tries to filter on `WHERE is_primary_provider = TRUE`.

### The Model Situation

The service file contains a comment: `# NOTE: Import your actual models when they're created`. This suggests the SQLAlchemy model for CareTeamAssignment may not exist yet, or exists elsewhere. We need to either:
1. Find the existing model and verify its schema
2. Create the model if it doesn't exist

The model needs to map to the `care_team_assignments` table with columns: id, organization_id, patient_id, provider_id, role, assigned_at, and removed_at (for soft deletes).

## Plan of Work

We will update the codebase in four phases:

### Phase 1: Create Type-Safe Role Enum

Define a CareTeamRole enum in a new file `apps/backend/src/models/enums.py` (or in the models file if it exists). This enum will:
- Inherit from `str` and `Enum` for SQLAlchemy compatibility
- Define constants: PRIMARY = "PRIMARY", SPECIALIST = "SPECIALIST", CONSULTANT = "CONSULTANT"
- Prevent typos and provide IDE autocomplete

### Phase 2: Locate or Create CareTeamAssignment Model

Either find the existing SQLAlchemy model or create it. The model must:
- Map to table name `care_team_assignments`
- Define column `role` as String, not a boolean `is_primary_provider`
- Include all columns from the DDL: id, organization_id, patient_id, provider_id, role, assigned_at, removed_at

### Phase 3: Update Service Layer

In `apps/backend/src/services/care_team_service.py`:

**File-wide changes:**
- Import the CareTeamRole enum
- Import the CareTeamAssignment model properly

**In `assign_primary_provider` method (lines 63-108):**
- Line 71: Change filter from `CareTeamAssignment.is_primary_provider == True` to `CareTeamAssignment.role == CareTeamRole.PRIMARY`
- Line 73: Change `values(is_primary_provider=False)` to `values(role=CareTeamRole.SPECIALIST)` (demote to SPECIALIST, not set to False)
- Line 87: Change `existing_assignment.is_primary_provider = True` to `existing_assignment.role = CareTeamRole.PRIMARY`
- Lines 90-94: Change the new_assignment creation to set `role=CareTeamRole.PRIMARY` instead of `is_primary_provider=True`
- Line 104: Update the constraint name check if it changed (verify constraint name is still `idx_unique_primary_provider_per_patient` or update to `uq_care_team_primary`)

**In `add_secondary_provider` method (lines 110-154):**
- Line 151: Change `is_primary_provider=False` to `role=CareTeamRole.SPECIALIST` (explicitly set role to SPECIALIST)

**In `get_primary_provider` method (lines 156-181):**
- Line 178: Change filter from `CareTeamAssignment.is_primary_provider == True` to `CareTeamAssignment.role == CareTeamRole.PRIMARY`

**In `remove_from_care_team` method (lines 183-216):**
- No changes needed - this method doesn't reference is_primary_provider

**Update docstrings:**
- Update method docstrings to mention "role='PRIMARY'" instead of "is_primary_provider=True" where appropriate
- Update examples in docstrings to reflect the new approach

### Phase 4: Update Test Suite

In `apps/backend/tests/services/test_care_team_constraints.py`:

**File-wide changes:**
- Import CareTeamRole enum at the top

**In all test methods that create CareTeamAssignment instances:**
- Replace `is_primary_provider=True` with `role=CareTeamRole.PRIMARY`
- Replace `is_primary_provider=False` with `role=CareTeamRole.SPECIALIST`

**In all test methods that query for primary providers:**
- Replace `CareTeamAssignment.is_primary_provider == True` with `CareTeamAssignment.role == CareTeamRole.PRIMARY`

**Specific test method updates:**
- `test_one_primary_provider_per_patient`: Update constraint name check on line 70 if constraint name changed
- `test_can_change_primary_by_updating_existing`: Lines 198-199, update to set role instead of boolean
- All database query filters throughout the file

### Phase 5: Update Documentation

**In `docs/PRIMARY_PROVIDER_CONSTRAINT.md`:**
- Replace examples showing `is_primary_provider=True` with `role=CareTeamRole.PRIMARY`
- Update SQL examples to show the actual role='PRIMARY' syntax
- Update the service layer examples to show the enum usage

**In `docs/04 - sql.ddl`:**
- Verify the schema already correctly shows role column (lines 124-142)
- Update comments if they reference is_primary_provider

## Concrete Steps

### Step 1: Verify Database Schema

From the repository root, connect to the database and verify the actual schema:

    psql $DATABASE_URL -c "\d care_team_assignments"

Expected output should show a `role` column of type VARCHAR or similar, NOT an `is_primary_provider` boolean column. If you see `is_primary_provider`, stop and investigate - the database may not match the documented schema.

### Step 2: Locate or Create SQLAlchemy Model

Search for the CareTeamAssignment model:

    cd apps/backend
    find src -name "*.py" -exec grep -l "class CareTeamAssignment" {} \;

If found: Read the file and verify it has a `role` column defined (not `is_primary_provider`).

If not found: Create the model. Create file `apps/backend/src/models/care_team.py`:

    from sqlalchemy import Column, String, DateTime, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID
    from src.models.base import Base  # Adjust import based on your base model location
    from datetime import datetime

    class CareTeamAssignment(Base):
        __tablename__ = "care_team_assignments"

        id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
        organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
        patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
        provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
        role = Column(String(50), nullable=False)  # 'PRIMARY', 'SPECIALIST', 'CONSULTANT'
        assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
        removed_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

### Step 3: Create Role Enum

If the file doesn't exist, create `apps/backend/src/models/enums.py`:

    from enum import Enum

    class CareTeamRole(str, Enum):
        """
        Role types for care team assignments.

        PRIMARY: The main provider accountable for patient care (only one per patient per org)
        SPECIALIST: A specialist consultant on the care team
        CONSULTANT: A consulting provider
        """
        PRIMARY = "PRIMARY"
        SPECIALIST = "SPECIALIST"
        CONSULTANT = "CONSULTANT"

If an enums file already exists, add the CareTeamRole class to it.

### Step 4: Update Service Layer

Edit `apps/backend/src/services/care_team_service.py`:

1. Add import at the top (after line 12):

        from src.models.enums import CareTeamRole
        from src.models.care_team import CareTeamAssignment  # Update the NOTE comment

2. Update `assign_primary_provider` method - replace the UPDATE statement (lines 66-74):

    OLD:
        await db.execute(
            update(CareTeamAssignment)
            .where(
                CareTeamAssignment.organization_id == organization_id,
                CareTeamAssignment.patient_id == patient_id,
                CareTeamAssignment.is_primary_provider == True
            )
            .values(is_primary_provider=False)
        )

    NEW:
        await db.execute(
            update(CareTeamAssignment)
            .where(
                CareTeamAssignment.organization_id == organization_id,
                CareTeamAssignment.patient_id == patient_id,
                CareTeamAssignment.role == CareTeamRole.PRIMARY
            )
            .values(role=CareTeamRole.SPECIALIST)
        )

3. Update line 87 in the same method:

    OLD: existing_assignment.is_primary_provider = True
    NEW: existing_assignment.role = CareTeamRole.PRIMARY

4. Update lines 90-94 in the same method:

    OLD:
        new_assignment = CareTeamAssignment(
            organization_id=organization_id,
            patient_id=patient_id,
            provider_id=provider_id,
            is_primary_provider=True
        )

    NEW:
        new_assignment = CareTeamAssignment(
            organization_id=organization_id,
            patient_id=patient_id,
            provider_id=provider_id,
            role=CareTeamRole.PRIMARY
        )

5. Update line 104 - verify constraint name matches actual constraint:

    Check if the constraint name in the error message matches. If the migration created `uq_care_team_primary` instead of `idx_unique_primary_provider_per_patient`, update the string check:

    OLD: if 'idx_unique_primary_provider_per_patient' in str(e):
    NEW: if 'uq_care_team_primary' in str(e):

6. Update `add_secondary_provider` method, line 151:

    OLD: is_primary_provider=False
    NEW: role=CareTeamRole.SPECIALIST

7. Update `get_primary_provider` method, line 178:

    OLD: CareTeamAssignment.is_primary_provider == True
    NEW: CareTeamAssignment.role == CareTeamRole.PRIMARY

8. Update docstrings to reflect role-based approach (optional but recommended for clarity).

### Step 5: Update Test Suite

Edit `apps/backend/tests/services/test_care_team_constraints.py`:

1. Add import at the top (around line 15):

        from src.models.enums import CareTeamRole
        from src.models.care_team import CareTeamAssignment

2. Update all instances of `is_primary_provider=True` to `role=CareTeamRole.PRIMARY`
3. Update all instances of `is_primary_provider=False` to `role=CareTeamRole.SPECIALIST`
4. Update all filter clauses like `CareTeamAssignment.is_primary_provider == True` to `CareTeamAssignment.role == CareTeamRole.PRIMARY`

Search and replace guide (do NOT use blind find-replace, verify each instance):
- Line 42: `is_primary_provider=True` → `role=CareTeamRole.PRIMARY`
- Line 51: `CareTeamAssignment.is_primary_provider == True` → `CareTeamAssignment.role == CareTeamRole.PRIMARY`
- Line 62: `is_primary_provider=True` → `role=CareTeamRole.PRIMARY`
- Line 70: Update constraint name if needed: `idx_unique_primary_provider_per_patient` → `uq_care_team_primary`
- Line 88: `is_primary_provider=False` → `role=CareTeamRole.SPECIALIST`
- Line 119: `is_primary_provider=True` → `role=CareTeamRole.PRIMARY`
- Line 129: `is_primary_provider=True` → `role=CareTeamRole.PRIMARY`
- Line 151: `is_primary_provider=True` → `role=CareTeamRole.PRIMARY`
- Line 162: `is_primary_provider=True` → `role=CareTeamRole.PRIMARY`
- Line 182: `is_primary_provider=True` → `role=CareTeamRole.PRIMARY`
- Line 192: `is_primary_provider=False` → `role=CareTeamRole.SPECIALIST`
- Line 198: `assignment1.is_primary_provider = False` → `assignment1.role = CareTeamRole.SPECIALIST`
- Line 199: `assignment2.is_primary_provider = True` → `assignment2.role = CareTeamRole.PRIMARY`
- Line 206: `CareTeamAssignment.is_primary_provider == True` → `CareTeamAssignment.role == CareTeamRole.PRIMARY`
- Line 266: `CareTeamAssignment.is_primary_provider == True` → `CareTeamAssignment.role == CareTeamRole.PRIMARY`

Continue for all occurrences in the file.

### Step 6: Update Documentation

Edit `docs/PRIMARY_PROVIDER_CONSTRAINT.md`:

Update code examples to show role-based approach. Key sections to update:
- Line 42: Update SQL to show actual constraint with `role = 'PRIMARY'`
- Lines 64-88: Update Python examples to use `role=CareTeamRole.PRIMARY`
- Lines 90-123: Update the "INCORRECT" and "CORRECT" examples
- Lines 224-281: Update scenario examples

The SQL examples should already be correct if they show `role = 'PRIMARY'`, but Python examples showing `is_primary_provider` should change to use the enum.

### Step 7: Run Tests

From the backend directory, run the test suite:

    cd apps/backend
    uv run pytest tests/services/test_care_team_constraints.py -v

Expected output: All tests should pass. If tests fail with "no such column: is_primary_provider", you missed an update. If tests fail with constraint name errors, verify the constraint name matches what's in the database.

### Step 8: Manual Database Verification

Connect to the database and verify the constraint is working with the role column:

    psql $DATABASE_URL

Then run these test queries:

    -- Test 1: Create test data
    INSERT INTO care_team_assignments (organization_id, patient_id, provider_id, role)
    VALUES
        (uuid_generate_v4(), uuid_generate_v4(), uuid_generate_v4(), 'PRIMARY')
    RETURNING id, organization_id, patient_id, role;

    -- Save the organization_id and patient_id from above, then test constraint:
    -- Test 2: Try to create duplicate primary (should FAIL)
    INSERT INTO care_team_assignments (organization_id, patient_id, provider_id, role)
    VALUES
        ('<org_id_from_above>', '<patient_id_from_above>', uuid_generate_v4(), 'PRIMARY');
    -- Expected: ERROR duplicate key value violates unique constraint "uq_care_team_primary"

    -- Test 3: Create secondary provider (should SUCCEED)
    INSERT INTO care_team_assignments (organization_id, patient_id, provider_id, role)
    VALUES
        ('<org_id_from_above>', '<patient_id_from_above>', uuid_generate_v4(), 'SPECIALIST');
    -- Expected: Success

    -- Clean up test data
    DELETE FROM care_team_assignments WHERE organization_id = '<org_id_from_above>';

## Validation and Acceptance

The implementation is successful when:

1. **Tests Pass**: Run `uv run pytest tests/services/test_care_team_constraints.py -v` and all tests pass
2. **Service Methods Work**: The service layer can:
   - Assign a primary provider using `assign_primary_provider()` - creates role='PRIMARY'
   - Add secondary providers using `add_secondary_provider()` - creates role='SPECIALIST'
   - Query for primary provider using `get_primary_provider()` - filters on role='PRIMARY'
   - Demote existing primary when assigning new primary
3. **Database Constraint Enforced**: Attempting to create a second PRIMARY assignment for the same (org, patient) fails with IntegrityError
4. **No References to is_primary_provider**: Grep the codebase for `is_primary_provider` and find zero results in service/test files:

       cd apps/backend
       grep -r "is_primary_provider" src/services/ tests/services/

   Expected: No results (or only in comments explaining the migration)

5. **Enum Provides Type Safety**: IDE autocomplete shows CareTeamRole.PRIMARY, .SPECIALIST, .CONSULTANT when typing `CareTeamRole.`

## Idempotence and Recovery

This change is safe to retry:
- If you've partially updated the files, you can continue from where you stopped
- The enum can be created multiple times (Python will just redefine it)
- The model can be imported multiple times without issues
- Tests can be run repeatedly to verify changes

To roll back:
- Use git to revert changes: `git checkout apps/backend/src/services/care_team_service.py`
- Delete the enum file if it was newly created: `rm apps/backend/src/models/enums.py`

However, note that the database schema already uses `role`, so rolling back the code means it won't work with the actual database. This migration should be completed, not rolled back.

## Artifacts and Notes

### Constraint Name Verification

Check the actual constraint name in the database:

    psql $DATABASE_URL -c "\d care_team_assignments"

Look for the unique index. It might be named either:
- `idx_unique_primary_provider_per_patient` (from the original migration)
- `uq_care_team_primary` (from the adapted migration)

Use the actual name in the service layer error handling.

### Example Test Output

After running tests successfully, you should see:

    tests/services/test_care_team_constraints.py::TestPrimaryProviderConstraint::test_one_primary_provider_per_patient PASSED
    tests/services/test_care_team_constraints.py::TestPrimaryProviderConstraint::test_multiple_non_primary_providers_allowed PASSED
    tests/services/test_care_team_constraints.py::TestPrimaryProviderConstraint::test_different_patients_can_have_same_primary_provider PASSED
    tests/services/test_care_team_constraints.py::TestPrimaryProviderConstraint::test_different_orgs_can_have_different_primaries PASSED
    tests/services/test_care_team_constraints.py::TestPrimaryProviderConstraint::test_can_change_primary_by_updating_existing PASSED
    tests/services/test_care_team_constraints.py::TestCareTeamService::test_assign_primary_provider_demotes_existing PASSED
    tests/services/test_care_team_constraints.py::TestCareTeamService::test_add_secondary_provider_does_not_affect_primary PASSED
    tests/services/test_care_team_constraints.py::TestCareTeamService::test_remove_provider_maintains_constraint PASSED

    ========== 8 passed in 2.34s ==========

### Grep Verification

After all updates, verify no references to the old column:

    cd apps/backend
    grep -rn "is_primary_provider" src/services/care_team_service.py tests/services/test_care_team_constraints.py

Expected: No results, or only in comments like "# Changed from is_primary_provider to role"

## Interfaces and Dependencies

### CareTeamRole Enum

In `apps/backend/src/models/enums.py` (or appropriate enums location):

    from enum import Enum

    class CareTeamRole(str, Enum):
        PRIMARY = "PRIMARY"
        SPECIALIST = "SPECIALIST"
        CONSULTANT = "CONSULTANT"

This enum inherits from both `str` and `Enum`, which:
- Allows SQLAlchemy to serialize it as a string automatically
- Provides IDE autocomplete and type checking
- Prevents typos like `role = "PRIMRY"` (will fail type check)
- Makes the code self-documenting

### CareTeamAssignment Model

In `apps/backend/src/models/care_team.py` (or wherever models are defined):

    from sqlalchemy import Column, String, DateTime
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.sql import text

    class CareTeamAssignment(Base):
        __tablename__ = "care_team_assignments"

        id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
        organization_id = Column(UUID(as_uuid=True), nullable=False)
        patient_id = Column(UUID(as_uuid=True), nullable=False)
        provider_id = Column(UUID(as_uuid=True), nullable=False)
        role = Column(String(50), nullable=False)
        assigned_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
        removed_at = Column(DateTime(timezone=True), nullable=True)

Key points:
- `role` is a String column (VARCHAR in PostgreSQL)
- We could use SQLAlchemy's Enum type for added type safety: `Column(Enum(CareTeamRole), nullable=False)`
- `removed_at` supports soft deletes (constraint excludes removed_at IS NOT NULL)

### Service Layer Interface

The `CareTeamService` class provides these methods:

    class CareTeamService:
        @staticmethod
        async def assign_primary_provider(
            db: AsyncSession,
            organization_id: UUID,
            patient_id: UUID,
            provider_id: UUID
        ) -> None:
            """Assign PRIMARY role to provider, demoting existing primary to SPECIALIST."""

        @staticmethod
        async def add_secondary_provider(
            db: AsyncSession,
            organization_id: UUID,
            patient_id: UUID,
            provider_id: UUID
        ) -> None:
            """Add provider with SPECIALIST role."""

        @staticmethod
        async def get_primary_provider(
            db: AsyncSession,
            organization_id: UUID,
            patient_id: UUID
        ) -> UUID | None:
            """Get provider_id where role='PRIMARY'."""

        @staticmethod
        async def remove_from_care_team(
            db: AsyncSession,
            organization_id: UUID,
            patient_id: UUID,
            provider_id: UUID
        ) -> bool:
            """Remove provider from care team (soft delete)."""

The interface remains identical; only the internal implementation changes from boolean to role string.

---

**Note**: This plan assumes the CareTeamAssignment model needs to be created or located. If it already exists with the correct schema, skip the model creation step and just verify it has a `role` column, not `is_primary_provider`.
