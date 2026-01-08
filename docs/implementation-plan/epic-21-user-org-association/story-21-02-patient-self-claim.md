# Story 21.2: Patient Self-Claim Flow
**User Story:** As a patient, I want to sign up and link my account to my existing patient record, so that I can access my health information online.

## Status
- [ ] **Pending**

## Context
- **API Ref:** NEW endpoint needed
- **DDL Ref:** `patients.user_id` (nullable FK to users)
- **Frontend Ref:** NEW pages/components needed

## Technical Specification
**Goal:** Allow patients to self-claim their record after signing up.

**Changes Required:**

### Backend

1.  **Endpoint:** `POST /api/v1/patients/claim` (NEW)
    - Request: `{ email: string, dob: date, medical_record_number?: string }`
    - Logic:
      - Find patient by email match in contact_methods OR by MRN+DOB
      - Verify patient.user_id is NULL (not already claimed)
      - Verify current_user.email matches patient contact email
      - Set patient.user_id = current_user.id
    - Returns: `PatientRead` on success
    - Errors: 404 if no match, 409 if already claimed

2.  **Endpoint:** `GET /api/v1/patients/me` (NEW)
    - Returns patient record(s) linked to current_user.id
    - Enables patient dashboard access

3.  **Schema:** `PatientClaimRequest` (NEW)
    ```python
    class PatientClaimRequest(BaseModel):
        dob: date
        last_four_ssn: str | None = None  # Optional extra verification
        medical_record_number: str | None = None
    ```

### Frontend

1.  **Route:** `/patient/claim` (NEW)
    - Form: DOB picker, optional MRN field
    - On success: redirect to patient dashboard

2.  **Component:** `PatientClaimForm.tsx` (NEW)
    - Verification UI with clear error messages

3.  **Patient Dashboard Access:**
    - If user has `patient_profile` via `useUserRole`, show patient features

### Security Considerations
- Rate limit claim attempts (prevent enumeration)
- Require email verification before claim
- Audit log all claim attempts (success and failure)
- Consider SMS/email verification code for extra security

## Acceptance Criteria
- [ ] Patient with no user_id can be claimed by matching user.
- [ ] Claim requires DOB verification at minimum.
- [ ] Already-claimed patients return 409 error.
- [ ] Mismatched DOB returns generic "not found" (no enumeration).
- [ ] Patient can view their own record after claiming.
- [ ] Claim attempt is audit logged.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_patient_claim.py::test_successful_claim`
- `pytest tests/api/test_patient_claim.py::test_already_claimed`
- `pytest tests/api/test_patient_claim.py::test_dob_mismatch`

**Manual Verification:**
- Create patient via admin, sign up as patient, claim record, verify access.
