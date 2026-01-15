# Story 19.1: Super Admin API
**User Story:** As a Super Admin, I want API access to manage the entire platform.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.4 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Super Admin Endpoints")

## Technical Specification
**Goal:** Implement platform-wide administration APIs.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/admin.py` (UPDATE)
    - `OrganizationAdminRead` (id, name, member_count, patient_count, subscription_status, created_at)
    - `UserAdminRead` (id, email, is_super_admin, locked_until, last_login_at)
    - `SystemHealth` (db_status, redis_status, worker_status, metrics)

2.  **API Router:** `backend/src/api/admin.py` (UPDATE)
    - `GET /api/v1/super-admin/organizations`
      - List all organizations (platform-wide)
      - Pagination, search by name
    - `GET /api/v1/super-admin/organizations/{org_id}`
      - Org detail with stats
    - `PATCH /api/v1/super-admin/organizations/{org_id}`
      - Update org (suspend, activate)
    - `GET /api/v1/super-admin/users`
      - List all users (platform-wide)
      - Filter by locked, super_admin
    - `PATCH /api/v1/super-admin/users/{user_id}/unlock`
      - Clear locked_until and failed_login_attempts
    - `PATCH /api/v1/super-admin/users/{user_id}`
      - Toggle is_super_admin, deactivate
    - `GET /api/v1/super-admin/system`
      - System health and metrics
      - DB connection, Redis, worker queues

3.  **Authorization:**
    - All endpoints require `is_super_admin=True`
    - Actions audited with SUPER_ADMIN context

## Acceptance Criteria
- [ ] `GET /super-admin/organizations` lists all orgs.
- [ ] `GET /super-admin/users` lists all users.
- [ ] Unlock clears lockout.
- [ ] System health returns status.
- [ ] Non-super-admin gets 403.
- [ ] All actions audited.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_super_admin.py`

**Manual Verification:**
- Lock user, unlock via API.
- Check system health endpoint.
