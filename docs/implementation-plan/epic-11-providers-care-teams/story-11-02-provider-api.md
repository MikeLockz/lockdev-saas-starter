# Story 11.2: Provider & Staff API
**User Story:** As an Admin, I want to manage provider and staff profiles, so that I can track my organization's team.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.2 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Providers", "Staff")

## Technical Specification
**Goal:** Implement provider and staff CRUD endpoints.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/providers.py` (NEW)
    - `ProviderCreate` (user_id, npi_number, specialty, license_number, license_state)
    - `ProviderRead` (id, user info, all provider fields)
    - `ProviderUpdate` (specialty, license updates)
    - `StaffCreate` (user_id, job_title, department)
    - `StaffRead`, `StaffUpdate`

2.  **API Router:** `backend/src/api/providers.py` (NEW)
    - `GET /api/v1/organizations/{org_id}/providers`
      - List all providers in org
    - `POST /api/v1/organizations/{org_id}/providers`
      - Promote user to provider role
      - Validate NPI format
    - `GET /api/v1/organizations/{org_id}/providers/{provider_id}`
    - `PATCH /api/v1/organizations/{org_id}/providers/{provider_id}`
    - `DELETE /api/v1/organizations/{org_id}/providers/{provider_id}`
      - Soft delete (set is_active=false)

3.  **API Router:** `backend/src/api/staff.py` (NEW)
    - Similar CRUD for staff profiles

4.  **NPI Validation:** `backend/src/utils/npi.py` (NEW)
    - `validate_npi(npi: str) -> bool` - Luhn algorithm check
    - Raise `HTTPException` if invalid

## Acceptance Criteria
- [ ] `POST /providers` creates provider with NPI validation.
- [ ] Duplicate NPI in same org returns 409 Conflict.
- [ ] `GET /providers` lists all active providers.
- [ ] Staff endpoints mirror provider functionality.
- [ ] Admin role required for all operations.
- [ ] Audit logs capture provider changes.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_providers.py::test_create_provider`
- `pytest tests/api/test_providers.py::test_duplicate_npi_rejected`
- `pytest tests/utils/test_npi.py::test_luhn_validation`

**Manual Verification:**
- Create provider with valid NPI.
- Try invalid NPI, verify rejection.
