# Story 20.4: Timezone Settings UI
**User Story:** As an Admin, I want to set my organization's timezone, and as a User, I want to optionally override it.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Epic 20 - Timezone Support
- **Dependencies:** Story 20.2 (Timezone API), Story 20.3 (Timezone Utilities)

## Technical Specification
**Goal:** Add timezone selection to organization settings and user profile.

**Changes Required:**

1.  **Timezone Selector Component:** `frontend/src/components/settings/TimezoneSelector.tsx` (NEW)
    ```typescript
    interface TimezoneSelectorProps {
      value: string;
      onChange: (tz: string) => void;
      disabled?: boolean;
    }
    ```
    - Dropdown with common timezones grouped by region
    - Search/filter functionality
    - Show UTC offset (e.g., "America/New_York (UTC-5)")

2.  **Organization Settings:** `frontend/src/routes/_auth/settings/organization.tsx` (UPDATE)
    - Add timezone selector in settings form
    - Save via organization update API
    - Show current timezone with visual indicator

3.  **User Profile Settings:** `frontend/src/routes/_auth/settings/profile.tsx` (UPDATE)
    - Add optional timezone override
    - Toggle: "Use organization timezone" / "Set custom timezone"
    - Clear button to reset to org default

4.  **Timezone Display Component:** `frontend/src/components/common/TimezoneDisplay.tsx` (NEW)
    - Show current effective timezone in header/footer
    - Format: "Times shown in Eastern Time (UTC-5)"
    - Click to open timezone settings

5.  **Super Admin Org Edit:** `frontend/src/routes/_auth/super-admin/organizations.tsx` (UPDATE)
    - Include timezone in org edit modal

## Acceptance Criteria
- [ ] TimezoneSelector dropdown works with search.
- [ ] Organization settings show timezone selector.
- [ ] Organization timezone updates via API.
- [ ] User profile has timezone override option.
- [ ] User timezone preference saves correctly.
- [ ] Timezone display shows current timezone.
- [ ] Super admin can edit org timezone.

## Verification Plan
**Automated Tests:**
- Browser-based tests for timezone selection (if applicable)

**Manual Verification:**
1. Go to Organization Settings.
2. Change timezone from "America/New_York" to "America/Los_Angeles".
3. Verify all appointment times now show Pacific Time.
4. Go to User Profile, set custom timezone to "Europe/London".
5. Verify times now show in GMT/BST.
6. Clear user override, verify times revert to org timezone.
