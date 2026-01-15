# Story 2.8: Internal Admin Panel
**User Story:** As a Developer, I want a quick admin interface to manage data during development and support.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 2.8 from `docs/03`

## Technical Specification
**Goal:** Configure `sqladmin`.

**Changes Required:**
1.  **File:** `backend/src/admin.py`
    - Configure `sqladmin.Admin`.
    - Add views for `User`, `Organization`, `Patient` (Limited columns).
    - **Security:** Protect route `/admin` with `ADMIN` role check.
2.  **File:** `backend/src/main.py`
    - Mount the admin app.

## Acceptance Criteria
- [ ] `/admin` is accessible only to Admin users.
- [ ] Can view/edit basic models.
- [ ] PHI is minimized in list views.

## Verification Plan
**Manual Verification:**
- Navigate to `/admin` as normal user -> 403/Redirect.
- Navigate to `/admin` as admin -> Dashboard loads.
