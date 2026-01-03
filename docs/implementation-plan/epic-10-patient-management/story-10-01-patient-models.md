# Story 10.1: Patient Models & Migration
**User Story:** As a Developer, I want patient database models, so that I can build the patient management feature.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.1 from `docs/10 - application implementation plan.md`
- **DDL Ref:** `docs/04 - sql.ddl` (Lines 114-145: `patients`, `organization_patients`, `contact_methods`)
- **Existing:** `Patient` model exists in `backend/src/models/profiles.py`, `OrganizationPatient` in `organizations.py`

## Technical Specification
**Goal:** Ensure patient models are complete and create contact_methods table.

**Changes Required:**

1.  **Review/Update:** `backend/src/models/profiles.py`
    - Ensure `Patient` model has all fields from DDL:
      - `id`, `user_id` (optional FK), `first_name`, `last_name`
      - `date_of_birth`, `gender`, `mrn` (medical record number)
      - `ssn_last_four`, `preferred_language`
      - Relationships to `organizations`, `contact_methods`

2.  **Migration:** `backend/migrations/versions/xxx_contact_methods.py`
    - Create `contact_methods` table:
      - `id` (UUID, PK)
      - `patient_id` (FK to patients)
      - `type` (String: PHONE, EMAIL, SMS)
      - `value` (String, the actual contact)
      - `is_primary` (Boolean)
      - `is_safe_for_voicemail` (Boolean, HIPAA flag)
      - `label` (String: Home, Work, Mobile)
      - `created_at`, `updated_at`

3.  **Model:** `backend/src/models/contacts.py` (NEW)
    - `ContactMethod` SQLAlchemy model

4.  **Indexes:** 
    - Trigram index on `patients.last_name` for fuzzy search
    - Index on `patients.date_of_birth`
    - Index on `patients.mrn`

## Acceptance Criteria
- [x] `Patient` model has all required fields.
- [x] `ContactMethod` model created with relationships.
- [x] Migration runs successfully.
- [x] Trigram extension enabled (pg_trgm).
- [x] Models exported in `__init__.py`.

## Verification Plan
**Automated Tests:**
- `pytest tests/models/test_patient.py` - Model creation
- `alembic upgrade head` runs without errors

**Manual Verification:**
- Connect to DB, verify tables and indexes exist.
