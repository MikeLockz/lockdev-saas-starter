# Story 14.2: Proxy API
**User Story:** As a Patient, I want to manage who can access my records via API.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.1 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Proxies")

## Technical Specification
**Goal:** Implement proxy assignment and permission management.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/proxies.py` (NEW)
    - `ProxyAssignmentCreate` (email, relationship, permissions dict)
    - `ProxyAssignmentRead` (all fields + proxy user info)
    - `ProxyPermissions` (all boolean flags)
    - `ProxyPatientRead` (patient info for proxy dashboard)

2.  **API Router:** `backend/src/api/proxies.py` (NEW)
    - `GET /api/v1/organizations/{org_id}/patients/{patient_id}/proxies`
      - List all proxies for a patient
    - `POST /api/v1/organizations/{org_id}/patients/{patient_id}/proxies`
      - Assign proxy by email (existing user or invite)
      - Set initial permissions
    - `PATCH .../proxies/{assignment_id}`
      - Update permissions
    - `DELETE .../proxies/{assignment_id}`
      - Revoke access (soft delete with revoked_at)
    - `GET /api/v1/users/me/proxy/patients`
      - List patients the current user is proxy for

3.  **Auth Update:** `backend/src/security/auth.py`
    - `get_patient_access(patient_id)` dependency
    - Check org membership OR proxy assignment
    - Return access level (permission dict)

4.  **Business Logic:**
    - Email existing user → immediate access
    - Email new user → send invite, grant on accept
    - Audit log all access grants/revocations

## Acceptance Criteria
- [ ] `POST /proxies` assigns proxy with permissions.
- [ ] `PATCH /proxies/{id}` updates permissions.
- [ ] `DELETE /proxies/{id}` revokes access.
- [ ] Proxy can access patient based on permissions.
- [ ] Non-proxy user gets 403 on patient routes.
- [ ] Audit log captures all proxy changes.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_proxies.py::test_assign_proxy`
- `pytest tests/api/test_proxies.py::test_permission_enforcement`

**Manual Verification:**
- Assign proxy, log in as proxy, verify access.
