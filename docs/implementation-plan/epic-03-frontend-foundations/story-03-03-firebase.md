# Story 3.3: Firebase Client Auth
**User Story:** As a User, I want to log in using my credentials, so that I can access my data.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 3.3 from `docs/03`

## Technical Specification
**Goal:** Integrate Firebase Auth SDK.

**Changes Required:**
1.  **File:** `frontend/src/lib/firebase.ts`
    - Initialize app with env vars.
2.  **Hook:** `frontend/src/hooks/useAuth.ts`
    - Wrapper around `react-firebase-hooks`.
    - Expose `user`, `loading`, `signIn`, `signOut`.

## Acceptance Criteria
- [ ] `useAuth` returns user object after login.
- [ ] Token is available for API calls.

## Verification Plan
**Manual Verification:**
- Create a temporary login button. Log in with Google/Email. Check console for user object.
