# Story 9.1: API Hooks Infrastructure
**User Story:** As a Developer, I want standardized API hooks, so that all components fetch data consistently.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Steps 1.1-1.3 from `docs/10 - application implementation plan.md`
- **State Ref:** `docs/08 - front end state management.md`

## Technical Specification
**Goal:** Create React Query hooks for all API endpoints with proper auth handling.

**Changes Required:**

1.  **API Client Update:** `frontend/src/lib/axios.ts`
    - Add request interceptor for JWT token
    - Get token from Firebase `auth.currentUser.getIdToken()`
    - Set `Authorization: Bearer <token>` header
    - Handle 401 responses (logout / refresh)

2.  **Query Client:** `frontend/src/lib/query-client.ts`
    - Configure defaults (staleTime, refetchOnWindowFocus)
    - Add global error handler

3.  **Hooks:** `frontend/src/hooks/api/`
    - `useCurrentUser.ts` - GET /api/v1/me
    - `useOrganizations.ts` - GET /api/v1/organizations
    - `useOrgMembers.ts` - GET /api/v1/organizations/:id/members
    - `useRequiredConsents.ts` - GET /api/v1/consent/required
    - Pattern: Each hook exports `useXxx()` query and `useUpdateXxx()` mutation

4.  **Types:** Leverage `frontend/src/lib/api-types.d.ts`
    - Ensure all hooks use generated types
    - Add missing types if needed

5.  **App Provider:** `frontend/src/main.tsx`
    - Ensure QueryClientProvider wraps app
    - Add auth state synchronization

## Acceptance Criteria
- [x] All API requests include JWT token when authenticated.
- [x] 401 response triggers logout flow.
- [x] Hooks use proper TypeScript types.
- [x] Loading states returned from hooks.
- [x] Errors captured and available from hooks.
- [x] Data cached and reused across components.

## Verification Plan
**Automated Tests:**
- `pnpm test -- useCurrentUser` (hook test with MSW)
- `pnpm test -- api-interceptor` (auth header test)

**Manual Verification:**
- Open DevTools Network tab, verify Authorization header.
- Refresh page, verify data from cache first.
