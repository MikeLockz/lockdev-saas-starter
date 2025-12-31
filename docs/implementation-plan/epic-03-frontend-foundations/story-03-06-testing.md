# Story 3.6: Testing & Data Seeding
**User Story:** As a QA Engineer, I want automated tests and deterministic seed data, so that I can verify features reliably.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 3.6 from `docs/03`

## Technical Specification
**Goal:** Setup Vitest and Playwright.

**Changes Required:**
1.  **File:** `frontend/vitest.config.ts`.
2.  **File:** `backend/scripts/seed_e2e.py`
    - Creates "Test Patient" and "Test Staff".
3.  **File:** `frontend/playwright.config.ts`
    - `globalSetup` runs seed script.

## Acceptance Criteria
- [ ] `pnpm vitest` runs.
- [ ] `pnpm playwright test` runs and logs in as seeded user.

## Verification Plan
**Automated Tests:**
- Run the full test suite.
