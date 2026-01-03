# Story 11.1: Provider & Staff Models
**User Story:** As a Developer, I want provider and staff database models, so that I can track clinical roles.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.2 from `docs/10 - application implementation plan.md`
- **DDL Ref:** `docs/04 - sql.ddl` (Lines 88-111: `providers`, `staff`)
- **Existing:** Models exist in `backend/src/models/profiles.py`

## Technical Specification
**Goal:** Ensure provider/staff models are complete and add care team assignments.

**Changes Required:**

1.  **Review/Update:** `backend/src/models/profiles.py`
    - `Provider` model:
      - `id`, `user_id` (FK), `organization_id` (FK)
      - `npi_number` (unique per org), `specialty`
      - `license_number`, `license_state`
      - `is_active`, `created_at`, `updated_at`
    - `Staff` model:
      - `id`, `user_id` (FK), `organization_id` (FK)
      - `job_title`, `department`
      - `is_active`, `created_at`, `updated_at`

2.  **Migration:** `backend/migrations/versions/xxx_care_team_assignments.py`
    - Create `care_team_assignments` table:
      - `id` (UUID, PK)
      - `patient_id` (FK to patients)
      - `provider_id` (FK to providers)
      - `role` (String: PRIMARY, SPECIALIST, CONSULTANT)
      - `assigned_at`, `removed_at`
      - Unique constraint on `(patient_id, provider_id)` where active

3.  **Model:** `backend/src/models/care_teams.py` (NEW)
    - `CareTeamAssignment` SQLAlchemy model

4.  **Validation:**
    - NPI format validation (10 digits, Luhn check)
    - Unique NPI within organization

## Acceptance Criteria
- [ ] `Provider` model has NPI, specialty, license fields.
- [ ] `Staff` model has job title, department fields.
- [ ] `CareTeamAssignment` model created.
- [ ] NPI uniqueness enforced.
- [ ] Migration runs successfully.

## Verification Plan
**Automated Tests:**
- `pytest tests/models/test_provider.py` - NPI validation

**Manual Verification:**
- Create provider in DB, verify fields.
