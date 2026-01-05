# Story 20.3: Timezone Frontend Utilities
**User Story:** As a Developer, I want reusable timezone utilities so that all components display dates consistently.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Epic 20 - Timezone Support
- **Dependencies:** Story 20.2 (Timezone API)

## Technical Specification
**Goal:** Create timezone context, utilities, and update all date-displaying components.

**Changes Required:**

1.  **Install Dependency:**
    ```bash
    cd frontend && pnpm add date-fns-tz
    ```

2.  **Timezone Utilities:** `frontend/src/lib/timezone.ts` (NEW)
    ```typescript
    import { formatInTimeZone, toZonedTime } from 'date-fns-tz';

    export function formatDateTime(
      date: Date | string,
      formatStr: string,
      timezone: string
    ): string {
      return formatInTimeZone(date, timezone, formatStr);
    }

    export function formatRelativeTime(
      date: Date | string,
      timezone: string
    ): string {
      const zonedDate = toZonedTime(date, timezone);
      return formatDistanceToNow(zonedDate, { addSuffix: true });
    }
    ```

3.  **Timezone Hook:** `frontend/src/hooks/useTimezone.ts` (NEW)
    ```typescript
    export function useTimezone(): string {
      const { data: user } = useCurrentUser();
      return user?.effective_timezone || 'UTC';
    }
    ```

4.  **Timezone Context:** `frontend/src/contexts/TimezoneContext.tsx` (NEW)
    ```typescript
    const TimezoneContext = createContext<string>('UTC');

    export function TimezoneProvider({ children }) {
      const timezone = useTimezone();
      return (
        <TimezoneContext.Provider value={timezone}>
          {children}
        </TimezoneContext.Provider>
      );
    }
    ```

5.  **Component Updates:** Update all components using `date-fns`:
    | Component | Change |
    | :--- | :--- |
    | `AppointmentCard.tsx` | Use `formatDateTime` with timezone |
    | `AppointmentList.tsx` | Use timezone-aware formatting |
    | `AppointmentCreateModal.tsx` | Convert inputs to UTC |
    | `CallCenterDashboard.tsx` | Use timezone-aware display |
    | `CareTeamList.tsx` | Use timezone-aware display |
    | `DocumentList.tsx` | Use timezone-aware display |
    | `MemberTable.tsx` | Use timezone-aware display |
    | `NotificationItem.tsx` | Use timezone-aware relative time |
    | `PatientTable.tsx` | Use timezone-aware display |
    | `TaskBoard.tsx` | Use timezone-aware display |
    | `ThreadList.tsx` | Use timezone-aware relative time |
    | `ChatInterface.tsx` | Use timezone-aware relative time |
    | `patients/$patientId.tsx` | Use timezone-aware display |

6.  **Provider Integration:** `frontend/src/App.tsx` or root layout (UPDATE)
    - Wrap app in `TimezoneProvider`

## Acceptance Criteria
- [ ] `date-fns-tz` installed.
- [ ] Timezone utilities work correctly.
- [ ] useTimezone hook returns effective timezone.
- [ ] All 13+ components updated to use timezone.
- [ ] Dates display in user's configured timezone.
- [ ] Audit log viewer continues to show UTC.

## Verification Plan
**Automated Tests:**
- `pnpm test -- timezone` (new unit tests for utilities)

**Manual Verification:**
- Set org timezone to "America/Los_Angeles".
- Verify appointment times display in PT.
- Compare with UTC stored in database.
