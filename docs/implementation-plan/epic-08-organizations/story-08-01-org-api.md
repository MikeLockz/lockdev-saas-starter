# Story 8.1: Organization CRUD API
**User Story:** As a User, I want to create and manage organizations, so that I can set up my practice.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.3 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Organizations")
- **Models:** `Organization`, `OrganizationMember` already exist in `backend/src/models/organizations.py`

## Technical Specification
**Goal:** Implement organization CRUD endpoints.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/organizations.py` (NEW)
    - `OrganizationCreate` (name, tax_id?)
    - `OrganizationRead` (id, name, tax_id, subscription_status, member_count, patient_count)
    - `OrganizationUpdate` (name, settings_json)
    - `MemberRead` (id, user_id, email, display_name, role, created_at)

2.  **API Router:** `backend/src/api/organizations.py` (NEW)
    - `GET /api/v1/organizations` - List user's organizations
      - Query user's memberships, return orgs
    - `POST /api/v1/organizations` - Create organization
      - Create org + OrganizationMember with role=ADMIN
    - `GET /api/v1/organizations/{org_id}` - Get org details
      - Require membership
    - `PATCH /api/v1/organizations/{org_id}` - Update org
      - Require ADMIN role
    - `GET /api/v1/organizations/{org_id}/members` - List members
      - Require membership

3.  **Dependency:** `backend/src/security/org_access.py` (NEW)
    - `get_current_org_member(org_id)` - Validates user is member of org
    - Returns `OrganizationMember` with role
    - `require_org_admin(org_id)` - Validates ADMIN role

4.  **Main Router:** `backend/src/main.py`
    - Include organizations router

## Acceptance Criteria
- [x] `GET /organizations` returns user's orgs only.
- [x] `POST /organizations` creates org with user as ADMIN.
- [x] `GET /organizations/{id}` returns 403 for non-members.
- [x] `GET /organizations/{id}/members` lists all members.
- [x] Audit logs capture org creation and updates.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_organizations.py::test_list_orgs`
- `pytest tests/api/test_organizations.py::test_create_org`
- `pytest tests/api/test_organizations.py::test_access_denied_non_member`
- `pytest tests/api/test_organizations.py::test_list_members`

**Manual Verification:**
- Create org via API, verify in database.
- List orgs, verify only user's orgs returned.
