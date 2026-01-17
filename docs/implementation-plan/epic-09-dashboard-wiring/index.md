# Epic 9: Dashboard Wiring
**User Story:** As a User, I want the dashboard to show real data from the backend, so that the UI is functional and useful.

**Goal:** Connect frontend components to backend APIs with proper data fetching, caching, and state management.

## Traceability Matrix
| Plan Step (docs/10) | Story File | Status |
| :--- | :--- | :--- |
| Step 1.1-1.2 (API Hooks) | `story-09-01-api-hooks.md` | Done |
| Step 1.2 (Dashboard Data) | `story-09-02-dashboard-data.md` | Done |
| Step 1.1.5 (Consent Flow) | `story-09-03-consent-flow.md` | Done |

## Execution Order
1.  [x] `story-09-01-api-hooks.md`
2.  [x] `story-09-02-dashboard-data.md`
3.  [x] `story-09-03-consent-flow.md`

## Epic Verification
**Completion Criteria:**
- [x] All API calls use React Query hooks.
- [x] JWT token attached to authenticated requests.
- [x] Dashboard displays real user and org data.
- [x] Consent flow blocks access until signed.
- [x] Loading and error states handled gracefully.
