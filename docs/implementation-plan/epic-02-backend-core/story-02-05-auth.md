# Story 2.5: Authentication & GCIP
**User Story:** As a Security Engineer, I want secure authentication with MFA enforcement, so that we meet HIPAA requirements.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 2.5 from `docs/03`

## Technical Specification
**Goal:** Implement JWT verification and Context Injection.

**Changes Required:**
1.  **File:** `backend/src/security/auth.py`
    - Initialize `firebase-admin`.
    - `verify_token` dependency: Decodes JWT, checks expiry.
    - `get_current_user` dependency: Fetches User model from DB.
    - **MFA Check:** Middleware to check `auth_time` or MFA claims for Staff/Provider roles.
2.  **File:** `backend/src/middleware/context.py`
    - Extract `user_id` and `tenant_id` from token.
    - Set `contextvars` for RLS.

## Acceptance Criteria
- [ ] Valid JWT returns User object.
- [ ] Staff user without MFA is denied access to sensitive routes.
- [ ] Context variables are set for RLS.

## Verification Plan
**Automated Tests:**
- Unit test verifying token decoding.
- Test MFA logic: Scenarios where MFA is required vs optional.
