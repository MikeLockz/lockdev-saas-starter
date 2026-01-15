# Story 21.3: Admin Patient Link Flow
**User Story:** As an Organization Admin, I want to manually link a user account to a patient record, so that patients who contact support can gain access.

## Status
- [ ] **Pending**

## Context
- **API Ref:** NEW endpoint needed
- **DDL Ref:** `patients.user_id` (nullable FK to users)
- **Frontend Ref:** Patient detail page enhancement

## Technical Specification
**Goal:** Allow admins to link existing user accounts to patient records.

**Changes Required:**

### Backend

1.  **Endpoint:** `POST /api/v1/organizations/{org_id}/patients/{patient_id}/link-user` (NEW)
    - Request: `{ user_id: UUID }` or `{ user_email: string }`
    - Authorization: Requires ADMIN role in organization
    - Logic:
      - Verify patient exists in org (via OrganizationPatient)
      - Verify patient.user_id is NULL
      - Find user by ID or email
      - Set patient.user_id = user.id
    - Returns: `PatientRead`
    - Errors: 404 user not found, 409 already linked

2.  **Endpoint:** `DELETE /api/v1/organizations/{org_id}/patients/{patient_id}/link-user` (NEW)
    - Unlinks user from patient (sets user_id = NULL)
    - Use case: incorrect link, patient account transfer

3.  **Schema:**
    ```python
    class PatientLinkUserRequest(BaseModel):
        user_id: UUID | None = None
        user_email: str | None = None
        
        @model_validator(mode='after')
        def require_one(self):
            if not self.user_id and not self.user_email:
                raise ValueError('Either user_id or user_email required')
            return self
    ```

### Frontend

1.  **Patient Detail Enhancement:**
    - Show "Link User Account" button if `patient.user_id` is null
    - Modal: Search for user by email, display match, confirm link

2.  **Component:** `LinkUserModal.tsx` (NEW)
    - Email search input
    - User preview (name, email)
    - Confirm/Cancel buttons

3.  **Patient Detail Display:**
    - Show linked user info if `patient.user_id` is set
    - "Unlink" button for admins

## Acceptance Criteria
- [ ] Admin can search users by email.
- [ ] Admin can link found user to patient.
- [ ] Admin can unlink user from patient.
- [ ] Non-admin roles cannot link/unlink.
- [ ] Link action is audit logged.
- [ ] Patient with linked user shows user info in UI.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_patient_link.py::test_admin_link_user`
- `pytest tests/api/test_patient_link.py::test_non_admin_forbidden`
- `pytest tests/api/test_patient_link.py::test_unlink_user`

**Manual Verification:**
- Create patient, create separate user, admin links them, verify patient can now log in.
