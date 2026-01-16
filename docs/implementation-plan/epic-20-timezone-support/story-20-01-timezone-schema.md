# Story 20.1: Timezone Schema
**User Story:** As the system, I need to store timezone preferences for organizations and users.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Epic 20 - Timezone Support
- **Dependencies:** Epic 08 (Organizations), Epic 07 (User Identity)

## Technical Specification
**Goal:** Add timezone columns to Organization and User models.

**Changes Required:**

1.  **Migration:** `backend/alembic/versions/xxx_add_timezone_fields.py` (NEW)
    - Add `timezone` column to `organizations` table
      - Type: `VARCHAR(50)`
      - Default: `'America/New_York'`
      - Not nullable
    - Add `timezone` column to `users` table
      - Type: `VARCHAR(50)`
      - Nullable (null = use organization default)

2.  **Organization Model:** `backend/src/models/organizations.py` (UPDATE)
    ```python
    timezone: Mapped[str] = mapped_column(
        String(50), 
        default="America/New_York",
        nullable=False
    )
    ```

3.  **User Model:** `backend/src/models/users.py` (UPDATE)
    ```python
    timezone: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True
    )
    ```

4.  **Constants:** `backend/src/core/constants.py` (UPDATE)
    - Add `SUPPORTED_TIMEZONES` list with common IANA timezone identifiers
    - Add `DEFAULT_TIMEZONE = "America/New_York"`

## Acceptance Criteria
- [ ] Migration runs successfully.
- [ ] Organization has timezone with default value.
- [ ] User has nullable timezone field.
- [ ] Existing organizations get default timezone.
- [ ] Existing users get null timezone.

## Verification Plan
**Automated Tests:**
- `pytest tests/models/test_organization.py -k timezone` (new test)
- `pytest tests/models/test_user.py -k timezone` (new test)

**Manual Verification:**
- Run migration, verify columns exist in database.
- Create new org, verify default timezone applied.
