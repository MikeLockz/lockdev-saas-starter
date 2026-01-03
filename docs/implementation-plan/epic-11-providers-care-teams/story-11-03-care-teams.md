# Story 11.3: Care Team Management
**User Story:** As a Provider, I want to assign myself to a patient's care team, so that the patient knows who is treating them.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.2 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Care Team")

## Technical Specification
**Goal:** Implement care team assignment and viewing.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/care_teams.py` (NEW)
    - `CareTeamAssignmentCreate` (provider_id, role)
    - `CareTeamAssignmentRead` (id, provider details, role, assigned_at)

2.  **Endpoints:** `backend/src/api/patients.py`
    - `GET /api/v1/organizations/{org_id}/patients/{patient_id}/care-team`
      - List all assigned providers with roles
    - `POST /api/v1/organizations/{org_id}/patients/{patient_id}/care-team`
      - Assign provider to patient
      - Only one PRIMARY allowed
    - `DELETE .../care-team/{assignment_id}`
      - Remove provider from care team (soft delete)

3.  **Business Logic:**
    - Only one PRIMARY provider per patient
    - Cannot remove PRIMARY if patient has appointments with them
    - Provider must belong to same organization

4.  **Patient Portal View:**
    - `GET /api/v1/patients/me/care-team` (for patient users)
      - Returns their assigned providers

## Acceptance Criteria
- [ ] `GET /care-team` returns all assigned providers.
- [ ] `POST /care-team` assigns provider with role.
- [ ] Only one PRIMARY provider allowed.
- [ ] Provider must be in same organization.
- [ ] Patients can view their own care team.
- [ ] Audit log captures assignments.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_care_teams.py::test_assign_provider`
- `pytest tests/api/test_care_teams.py::test_only_one_primary`

**Manual Verification:**
- Assign provider to patient, verify in database.
- Try to assign second PRIMARY, verify error.
