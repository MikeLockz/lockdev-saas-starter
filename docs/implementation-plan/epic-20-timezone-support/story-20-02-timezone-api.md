# Story 20.2: Timezone API
**User Story:** As a User, I want the API to expose my effective timezone and allow updating preferences.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Epic 20 - Timezone Support
- **Dependencies:** Story 20.1 (Timezone Schema)

## Technical Specification
**Goal:** Expose timezone fields in API schemas and add a convenience endpoint.

**Changes Required:**

1.  **Organization Schemas:** `backend/src/schemas/organizations.py` (UPDATE)
    - Add `timezone: str` to `OrganizationRead`
    - Add `timezone: Optional[str]` to `OrganizationCreate`
    - Add `timezone: Optional[str]` to `OrganizationUpdate`

2.  **User Schemas:** `backend/src/schemas/users.py` (UPDATE)
    - Add `timezone: Optional[str]` to `UserRead`
    - Add `timezone: Optional[str]` to `UserUpdate`
    - Add `effective_timezone: str` computed field to `UserRead`

3.  **Timezone Endpoint:** `backend/src/api/users.py` (UPDATE)
    - `GET /api/v1/me/timezone`
      - Returns `{ "timezone": "America/New_York", "source": "organization" | "user" }`
      - Resolves: user.timezone ?? user.organization.timezone ?? "UTC"
    - `PATCH /api/v1/me/timezone`
      - Updates current user's timezone preference
      - Validates against `SUPPORTED_TIMEZONES`

4.  **Organization API:** `backend/src/api/organizations.py` (UPDATE)
    - Include timezone in PATCH operations
    - Validate against `SUPPORTED_TIMEZONES`

5.  **Validation Helper:** `backend/src/core/validators.py` (UPDATE)
    - Add `validate_timezone(tz: str) -> bool`
    - Use `zoneinfo.ZoneInfo` to validate IANA timezone names

## Acceptance Criteria
- [ ] Organization read includes timezone.
- [ ] User read includes timezone and effective_timezone.
- [ ] `/me/timezone` returns effective timezone with source.
- [ ] Invalid timezone returns 422 validation error.
- [ ] Organization update includes timezone.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_organizations.py -k timezone` (new tests)
- `pytest tests/api/test_users.py -k timezone` (new tests)

**Manual Verification:**
- Call `/me/timezone`, verify response.
- Update org timezone, verify user's effective timezone changes.
