# Story 19.2: Super Admin Frontend
**User Story:** As a Super Admin, I want a dashboard to manage the platform.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.4 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/super-admin/*`)

## Technical Specification
**Goal:** Implement super admin dashboard and management UI.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/super-admin/`
    - `index.tsx` - Platform dashboard
    - `organizations.tsx` - Tenant list
    - `organizations/$orgId.tsx` - Org detail
    - `users.tsx` - User list
    - `users/$userId.tsx` - User detail

2.  **Components:** `frontend/src/components/super-admin/`
    - `PlatformDashboard.tsx`
      - Key metrics: total orgs, users, revenue
      - System health status
      - Recent activity
    - `TenantList.tsx`
      - All organizations table
      - Status, member count, subscription
      - Actions: view, suspend
    - `TenantDetail.tsx`
      - Org overview
      - Member list
      - Actions: activate, suspend
    - `UserManagementTable.tsx`
      - All users table
      - Locked status, last login
      - Actions: unlock, toggle admin
    - `SystemHealthCard.tsx`
      - DB, Redis, worker status
      - Color-coded indicators

3.  **Hooks:** `frontend/src/hooks/api/`
    - `useSuperAdminOrgs.ts`
    - `useSuperAdminUsers.ts`
    - `useSystemHealth.ts`

4.  **Navigation:**
    - Super admin nav only visible to super admins
    - Separate from org-level admin

## Acceptance Criteria
- [ ] `/super-admin` shows platform metrics.
- [ ] `/super-admin/organizations` lists all tenants.
- [ ] `/super-admin/users` lists all users.
- [ ] Can unlock user from UI.
- [ ] System health displayed.
- [ ] Only super admins can access.

## Verification Plan
**Automated Tests:**
- `pnpm test -- PlatformDashboard`
- `pnpm test -- UserManagementTable`

**Manual Verification:**
- Log in as super admin, view dashboard.
- Unlock a locked user.
