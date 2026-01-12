# Review Findings - 2026-01-11

## Summary
Tested: 45+ routes | Issues: 28 | Not Implemented: 8

---

## Issues

### P0 - Critical

- **`/403`**: Page crashes with React error `useSidebar must be used within a SidebarProvider` - prevents proper unauthorized access handling
- **`/messages` API**: 404 errors for `GET /users/me/threads` and `POST /users/me/threads` - messaging functionality completely broken
- **Appointments Scheduling**: Patient users can see and select other patients (e.g., "Emma Johnson") in the scheduling modal - **security/privacy violation**

---

### P1 - Major

- **`/signup`**: Missing Terms of Service checkbox and Privacy Policy link - required for HIPAA compliance (Section 1.3)
- **`/appointments/new`**: Returns 404 - scheduling flow only available via modal on `/appointments` page (Section 5.2)
- **`/appointments/:appointmentId`**: No appointment detail route exists - no way to view, cancel, or reschedule individual appointments (Section 5.3)
- **`/appointments` calendar**: Appointments do not appear in calendar view even after creation - only visible on Dashboard (Section 5.1)
- **`/settings/*` sub-routes**: All routes 404 (`/settings/profile`, `/settings/security`, `/settings/security/password`, `/settings/security/mfa`, `/settings/communication`, `/settings/organizations`) - settings uses tabbed UI without URL routing (Section 9)
- **`/compliance/audit-logs`**: Returns 404 - correct route is `/admin/audit-logs` (Section 7.5)
- **Notifications "Mark all read"**: Button appears non-functional - does not update UI or badge count (Section 10.1)
- **Patient Dashboard**: Subscription status banner missing per docs (Section 3.1)
- **Proxy Dashboard**: Missing detailed appointment list across patients (only summary count), missing per-patient unread message indicators (Section 3.2)
- **Provider Dashboard**: Missing "Patient panel overview (new/active counts)" metric (Section 3.3)
- **Staff Dashboard**: Missing "Today's patient schedule" detail view (only summary count) (Section 3.4)

---

### P2 - Minor

- **Landing Page (`/`)**: Primary CTA is "Go to Dashboard" instead of documented "Get Started" (Section 1.1)
- **`/patients` list**: Missing "Primary Provider" column in table display (Section 4.1)
- **`/patients` list**: Displayed as table instead of cards per docs (Section 4.1)
- **`/patients/:patientId` header**: Missing patient photo and DOB in header (present in Overview tab) (Section 4.3)
- **`/patients` search**: Search by MRN may not filter results in real-time (Section 4.1)
- **`/admin/staff/new`**: Uses modal instead of dedicated route (Section 7.3)
- **`/admin/providers/new`**: Uses modal instead of dedicated route (Section 7.4)
- **Notifications page**: No type filters (Appointments, Messages, System) - only Unread/All filter in dropdown (Section 10.1)
- **Notifications page**: Filter uses dropdown instead of tabs (Section 10.1)
- **Notifications page header**: Missing notification bell icon that exists on Dashboard (Section 10.2)
- **All dashboards**: "Unread messages count" implemented as "Unread Notifications" aggregating all types (Sections 3.1-3.5)
- **Patient detail tabs**: Named "Overview, Contacts, Care Team, Appointments, Documents, Messages" vs documented "Overview, Documents, Care Team, Appointments, Messages" (Section 4.3)

---

## Not Implemented

| Route | Doc Reference |
|-------|---------------|
| `/appointments/:appointmentId` | Section 5.3 - Appointment detail view |
| `/appointments/:appointmentId/reschedule` | Section 5.4 - Reschedule appointment |
| `/messages/:threadId` | Section 6.3 - Message thread detail (API broken) |
| `/settings/profile` (standalone) | Section 9.2 - Uses tabs, not routes |
| `/settings/security/password` | Section 9.3 - Uses modal flow |
| `/settings/security/mfa` | Section 9.3 - Uses modal flow |
| `/super-admin/users/:id/unlock` | Section 8.3 - Unlock locked account |
| Type filters on notifications | Section 10.1 - Appointments/Messages/System |

---

## Test User Discrepancy

**Note**: Actual seed emails differ from documentation:

| Documented | Actual |
|------------|--------|
| `super_admin@lockdev.test` | `e2e@example.com` |
| `admin@acme-clinic.test` | (no dedicated org admin) |
| `provider@acme-clinic.test` | `provider@example.com` |
| `staff@acme-clinic.test` | `staff@example.com` |
| `patient@lockdev.test` | `patient@example.com` |
| `proxy@lockdev.test` | `proxy@example.com` |

---

## Verification Notes

- **Session Timeout (Section 2.1)**: Not tested (requires 15 min idle wait)
- **MFA Requirements (Section 2.2)**: MFA setup buttons present but not tested end-to-end
- **Real-Time Notifications SSE (Section 10.3)**: Not tested
- **Accessibility (Section 13)**: Not tested in this review
