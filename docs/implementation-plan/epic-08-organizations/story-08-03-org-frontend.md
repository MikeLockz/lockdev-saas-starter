# Story 8.3: Organization Frontend Components
**User Story:** As a User, I want to switch between my organizations and see member lists, so that I can manage my context.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.3 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md`
- **State Ref:** `docs/08 - front end state management.md`

## Technical Specification
**Goal:** Implement organization context management and display components.

**Changes Required:**

1.  **Store:** `frontend/src/store/org-store.ts` (NEW)
    - `useOrgStore` (Zustand)
      - `organizations: Organization[]`
      - `currentOrg: Organization | null`
      - `setOrganizations`, `setCurrentOrg`
    - Persist `currentOrg.id` to localStorage

2.  **Hooks:** `frontend/src/hooks/`
    - `useOrganizations.ts` - Query for user's organizations
    - `useOrgMembers.ts` - Query for org members
    - `useCurrentOrg.ts` - Convenience hook for active org

3.  **Components:** `frontend/src/components/org/`
    - `OrgSwitcher.tsx` - Dropdown in sidebar/header
      - Shows current org name
      - Lists all orgs on click
      - Changes context on selection
    - `MemberTable.tsx` - Data table with members
      - Columns: Name, Email, Role, Joined
      - Uses shadcn DataTable

4.  **Layout Update:** `frontend/src/components/layout/`
    - Add OrgSwitcher to sidebar header
    - Show current org name in header

5.  **API Client:** `frontend/src/lib/api-client.ts`
    - Add organization endpoints
    - Include `X-Organization-Id` header from store

## Acceptance Criteria
- [x] OrgSwitcher displays current organization.
- [x] Clicking OrgSwitcher shows dropdown of all orgs.
- [x] Selecting org updates context and persists.
- [x] MemberTable displays all org members.
- [x] Member roles displayed with proper formatting.
- [x] API calls include organization context.

## Verification Plan
**Automated Tests:**
- `pnpm test -- OrgSwitcher` (component test)
- `pnpm test -- MemberTable` (component test)

**Manual Verification:**
- Login, verify OrgSwitcher shows org.
- Create second org, verify switcher updates.
- Switch orgs, verify context changes.
