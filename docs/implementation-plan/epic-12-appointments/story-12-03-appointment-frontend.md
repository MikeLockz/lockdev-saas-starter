# Story 12.3: Appointment Frontend
**User Story:** As a Staff Member, I want a UI to view and create appointments.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.1 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/appointments`)

## Technical Specification
**Goal:** Implement appointment list and creation UI.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/appointments/`
    - `index.tsx` - Appointment list/calendar view

2.  **Components:** `frontend/src/components/appointments/`
    - `AppointmentList.tsx`
      - Table or card view of appointments
      - Date picker for filtering
      - Provider filter dropdown
      - Status badges (color-coded)
    - `AppointmentCreateModal.tsx`
      - Patient selector (async search)
      - Provider selector
      - Date/time picker
      - Duration selector
      - Appointment type
      - Reason field
    - `AppointmentCard.tsx`
      - Single appointment display
      - Quick actions: Confirm, Cancel, Complete
    - `AppointmentStatusBadge.tsx`
      - Color-coded status display

3.  **Hooks:** `frontend/src/hooks/api/`
    - `useAppointments.ts` - List with filter params
    - `useCreateAppointment.ts` - Mutation
    - `useUpdateAppointmentStatus.ts` - Status update mutation

4.  **Integration:**
    - Add to sidebar navigation
    - Add Appointments tab to PatientDetail (from Story 10.4)

## Acceptance Criteria
- [x] `/appointments` displays today's appointments by default.
- [x] Date filter changes displayed appointments.
- [x] Provider filter works correctly.
- [x] Create modal validates all required fields.
- [x] Status can be updated via quick actions.
- [x] Status badges show appropriate colors.

## Verification Plan
**Automated Tests:**
- `pnpm test -- AppointmentList`
- `pnpm test -- AppointmentCreateModal`

**Manual Verification:**
- Navigate to /appointments, verify list.
- Create new appointment via modal.
- Cancel an appointment, verify status update.
