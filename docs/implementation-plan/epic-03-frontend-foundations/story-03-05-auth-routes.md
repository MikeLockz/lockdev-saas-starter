# Story 3.5: Role-Based Route Protection
**User Story:** As a Security Engineer, I want to restrict access to pages based on user roles, so that patients cannot see staff views.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.5 from `docs/03`
- **Docs Ref:** `docs/06 - Frontend Views & Routes.md`

## Technical Specification
**Goal:** Implement `AuthGuard` and protected routes.

**Changes Required:**
1.  **Component:** `frontend/src/components/auth-guard.tsx`
    - Check `isAuthenticated`.
    - Check `user.roles` against `allowedRoles`.
    - Check `mfa_enabled` if `requireMfa` is true.
    - Check `requires_consent`.
2.  **Router:** Wrap sensitive routes in `_auth.tsx` layout using `AuthGuard`.

## Acceptance Criteria
- [x] Unauthenticated user -> Redirect to Login.
- [x] Patient accessing Staff route -> 403 / Redirect.
- [x] Unsigned consent -> Redirect to Consent.

## Verification Plan
**Manual Verification:**
- Try to access `/dashboard` without login.
- Log in as Patient, try to access `/admin`.
