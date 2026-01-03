# Story 9.2: Dashboard Real Data
**User Story:** As a User, I want the dashboard to display my real stats and activity, so that it's actually useful.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.2-1.3 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Route: /dashboard)

## Technical Specification
**Goal:** Replace mock data in dashboard with real API data.

**Changes Required:**

1.  **Backend Endpoint (Optional):** `backend/src/api/dashboard.py`
    - `GET /api/v1/dashboard/stats`
      - Return aggregated counts (patients, appointments today, etc.)
      - Scoped to current org
    - OR: Frontend aggregates from existing endpoints

2.  **Dashboard Update:** `frontend/src/routes/_auth/dashboard.tsx`
    - Replace hardcoded `stats` array with API data
    - Use `useCurrentUser()` for greeting
    - Use `useOrganizations()` for org context
    - Show loading skeleton while fetching

3.  **Components:**
    - `StatsCard.tsx` - Accept data as props
    - `ActivityFeed.tsx` - Fetch recent activity
      - Could use audit logs or placeholder until Phase 5

4.  **Error Handling:**
    - Show error state if API fails
    - Retry button

## Acceptance Criteria
- [x] Dashboard greeting shows real user name.
- [x] Stats cards show real data (or N/A if endpoint not ready).
- [x] Activity feed shows recent items or placeholder.
- [x] Loading skeleton shown while data fetches.
- [x] Error state displays if API fails.

## Verification Plan
**Automated Tests:**
- `pnpm test -- Dashboard` (component test with mocked hooks)

**Manual Verification:**
- Login, verify dashboard shows your name.
- Verify stats match database state.
