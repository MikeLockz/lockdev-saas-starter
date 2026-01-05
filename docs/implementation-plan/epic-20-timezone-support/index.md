# Epic 20: Timezone Support
**User Story:** As a User, I want dates and times displayed in my preferred timezone, so that I can understand when events occur relative to my location.

**Goal:** Implement organization-level and user-level timezone preferences with consistent timezone-aware display across all user-facing date/time fields.

## Traceability Matrix
| Plan Step (docs/10) | Story File | Status |
| :--- | :--- | :--- |
| Timezone Schema | `story-20-01-timezone-schema.md` | Pending |
| Timezone API | `story-20-02-timezone-api.md` | Pending |
| Timezone Frontend Utilities | `story-20-03-timezone-utilities.md` | Pending |
| Timezone Settings UI | `story-20-04-timezone-settings.md` | Pending |

## Execution Order
1.  [ ] `story-20-01-timezone-schema.md`
2.  [ ] `story-20-02-timezone-api.md`
3.  [ ] `story-20-03-timezone-utilities.md`
4.  [ ] `story-20-04-timezone-settings.md`

## Epic Verification
**Completion Criteria:**
- [ ] Organization model has timezone field.
- [ ] User model has optional timezone override.
- [ ] API returns user's effective timezone.
- [ ] All frontend date/time displays use configured timezone.
- [ ] Organization settings allow timezone selection.
- [ ] User profile allows timezone override.
- [ ] Audit logs continue to display UTC for compliance.
