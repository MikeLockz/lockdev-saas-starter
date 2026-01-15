# Story 14.1: Proxy Models & Migration
**User Story:** As a Developer, I want proxy assignment models with granular permissions.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.1 from `docs/10 - application implementation plan.md`
- **DDL Ref:** `docs/04 - sql.ddl` (Lines 132: `proxies`; 147-158: `patient_proxy_assignments`)
- **Existing:** `Proxy` model exists in `backend/src/models/profiles.py`

## Technical Specification
**Goal:** Ensure proxy models have granular permission fields.

**Changes Required:**

1.  **Review/Update:** `backend/src/models/assignments.py`
    - `PatientProxyAssignment` model:
      - `id` (UUID, PK)
      - `patient_id` (FK to patients)
      - `proxy_id` (FK to proxies)
      - `relationship` (String: PARENT, SPOUSE, GUARDIAN, CAREGIVER, OTHER)
      - **Permission Booleans:**
        - `can_view_profile` (Boolean, default True)
        - `can_view_appointments` (Boolean, default True)
        - `can_schedule_appointments` (Boolean, default False)
        - `can_view_clinical_notes` (Boolean, default False)
        - `can_view_billing` (Boolean, default False)
        - `can_message_providers` (Boolean, default False)
      - `granted_at`, `expires_at`, `revoked_at`

2.  **Update:** `backend/src/models/profiles.py`
    - Ensure `Proxy` model has `user_id` FK
    - Relationship to assignments

3.  **Indexes:**
    - Index on `proxy_id` for proxy dashboard
    - Index on `patient_id` for patient management

## Acceptance Criteria
- [ ] `PatientProxyAssignment` has all permission booleans.
- [ ] Relationship field captures proxy relationship.
- [ ] Expiration support for time-limited access.
- [ ] Models exported in `__init__.py`.

## Verification Plan
**Automated Tests:**
- `alembic upgrade head` runs without errors

**Manual Verification:**
- Create proxy assignment in DB, verify fields.
