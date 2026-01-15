# Story 7.4: User Settings Frontend
**User Story:** As a User, I want a settings page to manage my profile and security, so that I can control my account.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.2 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: /settings)
- **State Ref:** `docs/08 - front end state management.md`

## Technical Specification
**Goal:** Implement Settings UI with profile management, session monitoring, and MFA enrollment.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/settings/`
    - `index.tsx` - Settings layout with tabs
    - `profile.tsx` - Display name, email, avatar
    - `security.tsx` - Sessions list, MFA setup
    - `privacy.tsx` - Communication preferences

2.  **Components:** `frontend/src/components/settings/`
    - `ProfileForm.tsx` - Edit display name
    - `SessionList.tsx` - Show active sessions with revoke button
    - `MFASetup.tsx` - QR code display, code verification form
    - `PreferencesForm.tsx` - Toggle transactional/marketing consent

3.  **Hooks:** `frontend/src/hooks/`
    - `useUserProfile.ts` - Query for current user profile
    - `useSessions.ts` - Query/mutation for sessions
    - `useMFA.ts` - Mutations for setup/verify
    - `useSessionMonitor.ts` - Idle timeout detection (HIPAA)

4.  **Components:** `frontend/src/components/`
    - `SessionExpiryModal.tsx` - Warning modal before auto-logout

5.  **State Update:** `frontend/src/store/auth-store.ts`
    - Add session timeout configuration
    - Add idle tracking

## Acceptance Criteria
- [x] `/settings` route accessible to authenticated users.
- [x] Profile tab shows user info with edit capability.
- [x] Security tab shows active sessions with revoke buttons.
- [x] MFA setup shows QR code and verification input.
- [x] Privacy tab shows consent toggles.
- [x] Session expiry modal appears 5 minutes before timeout.
- [x] Idle for 15 minutes triggers logout (HIPAA).

## Verification Plan
**Automated Tests:**
- `pnpm test --filter settings` (Vitest component tests) - **PASSED**

**Manual Verification:**
- Navigate to /settings, verify all tabs work.
- Revoke a session, verify logout in other browser.
- Enable MFA using authenticator app.
- Leave page idle, verify warning modal appears.
