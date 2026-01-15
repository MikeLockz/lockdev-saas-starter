# Story 12.1: Appointment Models & Migration
**User Story:** As a Developer, I want appointment database models, so that I can build the scheduling feature.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.1 from `docs/10 - application implementation plan.md`
- **DDL Ref:** `docs/04 - sql.ddl` (Lines 215-245: `appointments`)

## Technical Specification
**Goal:** Create appointment model with status workflow.

**Changes Required:**

1.  **Migration:** `backend/migrations/versions/xxx_appointments.py`
    - Create `appointments` table:
      - `id` (UUID, PK)
      - `organization_id` (FK to organizations)
      - `patient_id` (FK to patients)
      - `provider_id` (FK to providers)
      - `scheduled_at` (DateTime with timezone)
      - `duration_minutes` (Integer, default 30)
      - `status` (String: SCHEDULED, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW)
      - `appointment_type` (String: INITIAL, FOLLOW_UP, URGENT)
      - `reason` (Text, optional)
      - `notes` (Text, optional - provider notes after visit)
      - `cancelled_at`, `cancelled_by`, `cancellation_reason`
      - `created_at`, `updated_at`

2.  **Model:** `backend/src/models/appointments.py` (NEW)
    - `Appointment` SQLAlchemy model
    - Relationships to patient, provider, organization

3.  **Indexes:**
    - Index on `scheduled_at` for date queries
    - Index on `provider_id` for provider schedule
    - Index on `patient_id` for patient history
    - Composite index on `(organization_id, scheduled_at)`

## Acceptance Criteria
- [x] `Appointment` model has all required fields.
- [x] Status field has valid choices constraint.
- [x] Migration runs successfully.
- [x] Indexes created for query performance.
- [x] Model exported in `__init__.py`.

## Verification Plan
**Automated Tests:**
- `alembic upgrade head` runs without errors

**Manual Verification:**
- Connect to DB, verify table and indexes.
