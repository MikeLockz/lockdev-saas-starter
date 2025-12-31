# Story 3.4: Async State Management
**User Story:** As a Developer, I want a structured way to handle API data and client state, so that the app is responsive and data-consistent.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 3.4 from `docs/03`
- **Docs Ref:** `docs/08 - front end state management.md`

## Technical Specification
**Goal:** Setup QueryClient and Zustand Stores.

**Changes Required:**
1.  **File:** `frontend/src/lib/query-client.ts`
    - Default options (staleTime 5m).
2.  **File:** `frontend/src/store/auth-store.ts` (Zustand)
    - Store `user` profile, `isAuthenticated`, `isImpersonating`.
    - Persist to `sessionStorage`.
3.  **File:** `frontend/src/store/ui-store.ts`
    - Toasts, Modals, Sidebar state.

## Acceptance Criteria
- [ ] QueryClient provider wraps app.
- [ ] Auth store persists session data.

## Verification Plan
**Manual Verification:**
- Check Redux DevTools (if using zustand middleware) or Console.
