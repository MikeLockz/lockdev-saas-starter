# Story 4.2b: Read Access Auditing
**User Story:** As a Compliance Officer, I want to know when Staff views a patient's record, not just when they edit it.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.2b from `docs/03`

## Technical Specification
**Goal:** Middleware to log READ access to sensitive routes.

**Changes Required:**
1.  **File:** `backend/src/middleware/audit.py`
    - Intercept `GET` requests to `/api/staff/*` and `/api/patients/*`.
    - Log `READ_ACCESS` event to `audit_logs` (via side-effect/background task to avoid blocking).

## Acceptance Criteria
- [ ] `GET /api/patients/{id}` creates an audit log entry.

## Verification Plan
**Manual Verification:**
- Make a GET request. Check DB logs.
