# Story 10.5: Patient Seeding
**User Story:** As a Developer, I want seed data with realistic patients, so that I can test the application effectively.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.1 from `docs/10 - application implementation plan.md`

## Technical Specification
**Goal:** Create seed script with 50 realistic dummy patients.

**Changes Required:**

1.  **Script:** `backend/scripts/seed_patients.py`
    - Generate 50 patients with realistic data (Faker)
    - Create OrganizationPatient enrollments
    - Add 1-3 contact methods per patient
    - Mix of safe/unsafe for voicemail
    - Various statuses (45 ACTIVE, 5 DISCHARGED)

2.  **Data Distribution:**
    - Names: Realistic with diverse backgrounds
    - DOB: Range from 1940-2020
    - Gender: M/F/Other/Prefer not to say
    - MRN: Auto-generated format (e.g., MRN-000001)
    - Languages: English (80%), Spanish (15%), Other (5%)

3.  **Makefile:** Add `make seed-patients` command

4.  **Integration:** Ensure seed works with existing E2E test user/org

## Acceptance Criteria
- [x] `make seed-patients` creates 50 patients.
- [x] Patients linked to test organization.
- [x] Each patient has at least one contact method.
- [x] Seed is idempotent (can run multiple times).
- [x] No PII/PHI from real people (HIPAA).

## Verification Plan
**Automated Tests:**
- Run seed script, verify count in database.

**Manual Verification:**
- Run seed, browse patient list in UI.
- Verify realistic data distribution.
