# Story 12.2: Appointment API
**User Story:** As a Staff Member, I want to create and manage appointments via API.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.1 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Appointments")

## Technical Specification
**Goal:** Implement appointment CRUD endpoints.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/appointments.py` (NEW)
    - `AppointmentCreate` (patient_id, provider_id, scheduled_at, duration_minutes, appointment_type, reason)
    - `AppointmentRead` (all fields + patient/provider names)
    - `AppointmentUpdate` (scheduled_at, duration, reason)
    - `AppointmentStatusUpdate` (status, cancellation_reason)
    - `AppointmentListParams` (date_from, date_to, provider_id, status)

2.  **API Router:** `backend/src/api/appointments.py` (NEW)
    - `GET /api/v1/organizations/{org_id}/appointments`
      - Filter by date range, provider, status
      - Pagination support
      - Default: today's appointments
    - `POST /api/v1/organizations/{org_id}/appointments`
      - Create new appointment
      - Validate no double-booking for provider
    - `GET /api/v1/organizations/{org_id}/appointments/{appointment_id}`
    - `PATCH /api/v1/organizations/{org_id}/appointments/{appointment_id}`
      - Update time, duration, reason
    - `PATCH /api/v1/organizations/{org_id}/appointments/{appointment_id}/status`
      - Update status (CONFIRMED, COMPLETED, CANCELLED, NO_SHOW)
      - Require reason for cancellation

3.  **Business Logic:**
    - Prevent double-booking same provider at same time
    - Only SCHEDULED appointments can be cancelled
    - COMPLETED status requires provider role

## Acceptance Criteria
- [x] `POST /appointments` creates appointment.
- [x] Double-booking returns 409 Conflict.
- [x] `GET /appointments` filters by date/provider.
- [x] Status update works with validation.
- [x] Cancellation requires reason.
- [x] Audit log captures appointment changes.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_appointments.py::test_create`
- `pytest tests/api/test_appointments.py::test_double_booking_rejected`
- `pytest tests/api/test_appointments.py::test_filter_by_date`

**Manual Verification:**
- Create appointment, verify in list.
- Try to book same slot twice.
