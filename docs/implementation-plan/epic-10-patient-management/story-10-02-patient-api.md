# Story 10.2: Patient CRUD API
**User Story:** As a Provider, I want to create, read, update patients via API, so that I can manage my patient roster.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.1 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Patients")

## Technical Specification
**Goal:** Implement patient CRUD endpoints scoped to organization.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/patients.py` (NEW)
    - `PatientCreate` (first_name, last_name, dob, gender, mrn, preferred_language)
    - `PatientRead` (id, all fields, contact_methods, enrolled_at)
    - `PatientUpdate` (partial update fields)
    - `PatientListItem` (subset for list view)
    - `PatientSearchParams` (name, mrn, dob range)

2.  **API Router:** `backend/src/api/patients.py` (NEW)
    - `POST /api/v1/organizations/{org_id}/patients`
      - Create patient + OrganizationPatient enrollment
      - Return PatientRead
    - `GET /api/v1/organizations/{org_id}/patients`
      - List with pagination (limit, offset)
      - Search by name (trigram), MRN, DOB
      - Filter by status (ACTIVE, DISCHARGED)
    - `GET /api/v1/organizations/{org_id}/patients/{patient_id}`
      - Full detail with contact methods
    - `PATCH /api/v1/organizations/{org_id}/patients/{patient_id}`
      - Update patient fields
    - `DELETE /api/v1/organizations/{org_id}/patients/{patient_id}`
      - Soft delete (set discharged_at)

3.  **Audit Middleware Integration:**
    - Set `resource_type='PATIENT'` in context
    - Set `resource_id=patient_id`
    - Automatic audit log on all operations

4.  **Main Router:** `backend/src/main.py`
    - Include patients router under organizations

## Acceptance Criteria
- [x] `POST /patients` creates patient and enrollment.
- [x] `GET /patients` returns paginated list.
- [x] Search by name uses fuzzy matching.
- [x] `GET /patients/{id}` returns full patient detail.
- [x] `PATCH /patients/{id}` updates allowed fields.
- [x] `DELETE /patients/{id}` sets discharged_at.
- [x] All operations logged to audit_logs.
- [x] Non-members get 403 Forbidden.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_patients.py::test_create_patient`
- `pytest tests/api/test_patients.py::test_list_patients`
- `pytest tests/api/test_patients.py::test_search_by_name`
- `pytest tests/api/test_patients.py::test_access_denied`

**Manual Verification:**
- Create patient via API, verify in database.
- Search for "Smi" returns "Smith" patients.
