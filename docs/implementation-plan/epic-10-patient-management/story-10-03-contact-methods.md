# Story 10.3: Contact Methods API
**User Story:** As a Staff Member, I want to manage patient contact methods with safety flags, so that I don't leave PHI on unsafe voicemails.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.1 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Contact Methods")
- **HIPAA:** `is_safe_for_voicemail` is critical for compliance

## Technical Specification
**Goal:** Implement contact method CRUD with primary contact logic.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/contacts.py` (NEW)
    - `ContactMethodCreate` (type, value, label, is_primary, is_safe_for_voicemail)
    - `ContactMethodRead` (id, all fields)
    - `ContactMethodUpdate` (partial)

2.  **Endpoints:** `backend/src/api/patients.py`
    - `GET /api/v1/organizations/{org_id}/patients/{patient_id}/contact-methods`
      - List all contact methods for patient
    - `POST /api/v1/organizations/{org_id}/patients/{patient_id}/contact-methods`
      - Add new contact method
      - If `is_primary=true`, unset other primaries of same type
    - `PATCH .../contact-methods/{contact_id}`
      - Update contact method
    - `DELETE .../contact-methods/{contact_id}`
      - Remove contact method
      - Cannot delete if it's the only primary

3.  **Business Logic:**
    - Each patient must have at least one primary PHONE contact
    - `is_safe_for_voicemail` defaults to `false` (conservative)
    - Switching primary unsets previous primary

## Acceptance Criteria
- [x] `POST /contact-methods` adds new contact.
- [x] Only one primary per contact type.
- [x] `is_safe_for_voicemail` can be toggled.
- [x] Cannot delete last primary contact.
- [x] Contact methods returned with patient detail.
- [x] Audit log captures contact changes.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_contacts.py::test_add_contact`
- `pytest tests/api/test_contacts.py::test_primary_switching`
- `pytest tests/api/test_contacts.py::test_cannot_delete_only_primary`

**Manual Verification:**
- Add phone, mark as primary, add another phone as primary.
- Verify first phone is no longer primary.
