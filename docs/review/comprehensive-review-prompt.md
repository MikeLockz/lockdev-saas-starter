# Comprehensive Documentation vs Implementation Review Prompt

> **Purpose**: Systematically verify that all documented requirements in `/docs` are correctly implemented in the actual application using browser-based testing.

---

## Output Requirements

**Output file**: `/docs/review/review-findings.md`

**ONLY report discrepancies.** Do not list passing tests.

### Output Format

```markdown
# Review Findings - [DATE]

## Summary
Tested: X routes | Issues: X | Not Implemented: X

## Issues

### P0 - Critical
- **[Route]**: [Actual] vs [Expected per doc section X]

### P1 - Major  
- **[Route]**: [Actual] vs [Expected per doc section X]

### P2 - Minor
- **[Route]**: [Actual] vs [Expected per doc section X]

## Not Implemented
- [Route]: [Doc reference]
```

### Rules
1. **Skip passing tests** - Only report issues
2. **Be specific** - State exact discrepancy  
3. **Reference docs** - Cite doc line/section
4. **No fluff** - Just facts, no explanations

---

## Pre-Requisites

Before testing, verify:

```bash
# 1. Application is running
make dev  # or docker compose up -d

# 2. Database is seeded with test data
cd backend && uv run python scripts/seed_e2e.py

# 3. Frontend is accessible
open http://localhost:5173
```

---

## Test Users Reference

From `seed_e2e.py`, verify these users exist for testing:

| Role | Email | Description |
|------|-------|-------------|
| Super Admin | `super_admin@lockdev.test` | Platform-wide access |
| Org Admin | `admin@acme-clinic.test` | Organization admin |
| Provider | `provider@acme-clinic.test` | Licensed clinician |
| Staff | `staff@acme-clinic.test` | Clinical/Admin staff |
| Patient | `patient@lockdev.test` | Self-managed patient |
| Proxy | `proxy@lockdev.test` | Manages dependent patients |

---

## Section 1: Public Routes Verification

### Test 1.1: Landing Page (`/`)
- [ ] Navigate to `http://localhost:5173/`
- [ ] Verify hero section with value proposition exists
- [ ] Verify "Login" and "Get Started" CTAs are present
- [ ] Verify links to Privacy Policy and Terms of Service work

### Test 1.2: Login Page (`/login`)
- [ ] Navigate to `/login`
- [ ] Verify email/password form
- [ ] Verify Google Sign-In button (if OAuth configured)
- [ ] Verify "Forgot Password" link → navigates to `/forgot-password`
- [ ] Verify "Create Account" link → navigates to `/signup`
- [ ] **Test**: Invalid credentials show error message
- [ ] **Test**: Successful login redirects to `/dashboard`

### Test 1.3: Signup Page (`/signup`)
- [ ] Navigate to `/signup`
- [ ] Verify registration form with email, password
- [ ] Verify Terms checkbox and Privacy link
- [ ] Verify redirect to `/dashboard` or `/consent` after registration

### Test 1.4: Forgot Password (`/forgot-password`)
- [ ] Navigate to `/forgot-password`
- [ ] Verify email input form
- [ ] Submit any email → Verify success message displayed
- [ ] Verify "Back to Login" link works

### Test 1.5: Legal Pages
- [ ] Navigate to `/legal/privacy` - Verify privacy policy text loads
- [ ] Navigate to `/legal/terms` - Verify terms of service text loads

---

## Section 2: Authentication & Security Verification

### Test 2.1: Session Timeout (Per Doc: 15 min)
- [ ] Login as any user
- [ ] Leave session idle for 13+ minutes
- [ ] Verify warning modal appears at 2 minutes before expiry
- [ ] Verify auto-logout after 15 minutes of inactivity
- [ ] Verify redirect to `/login?reason=timeout`

### Test 2.2: MFA Requirements
- [ ] Login as Provider/Staff/Admin user
- [ ] If MFA not enabled, verify redirect to `/settings/security/mfa`
- [ ] Verify blocking modal: "MFA is required for your role"
- [ ] Navigate to MFA setup → Verify QR code and backup codes displayed

### Test 2.3: Dev Login Buttons (Development Mode)
- [ ] On login page, verify dev login buttons for each role
- [ ] Click each dev login button → Verify successful authentication
- [ ] Verify correct role context after login

---

## Section 3: Dashboard Verification (Per Role)

### Test 3.1: Patient Dashboard
Login as: `patient@lockdev.test`

- [ ] Verify route: `/dashboard`
- [ ] **Content**: Upcoming appointments (next 3)
- [ ] **Content**: Unread messages count with preview
- [ ] **Content**: Care team quick contacts
- [ ] **Content**: Subscription status banner (if applicable)
- [ ] Verify Patient Overview Card displays:
  - Upcoming appointments with date, time, provider
  - "My Care Team" section with providers and specialties

### Test 3.2: Proxy Dashboard
Login as: `proxy@lockdev.test`

- [ ] Verify route: `/dashboard`
- [ ] **Content**: Quick access to managed patients (cards)
- [ ] **Content**: Upcoming appointments across all patients
- [ ] **Content**: Unread messages per patient
- [ ] Verify "My Patients" appears in sidebar navigation
- [ ] Navigate to `/proxy/patients` → Verify patient list

### Test 3.3: Provider Dashboard
Login as: `provider@acme-clinic.test`

- [ ] Verify route: `/dashboard`
- [ ] **Content**: Today's appointments (timeline view)
- [ ] **Content**: Unread messages count
- [ ] **Content**: Pending tasks/follow-ups
- [ ] **Content**: Patient panel overview (new/active counts)
- [ ] Verify Provider Overview Card displays

### Test 3.4: Staff Dashboard
Login as: `staff@acme-clinic.test`

- [ ] Verify route: `/dashboard`
- [ ] **Content**: Task queue
- [ ] **Content**: Today's patient schedule
- [ ] **Content**: Quick patient search
- [ ] Verify Staff Overview Card displays

### Test 3.5: Organization Admin Dashboard
Login as: `admin@acme-clinic.test`

- [ ] Verify route: `/dashboard`
- [ ] **Content**: Organization health metrics
- [ ] **Content**: Member activity summary
- [ ] **Content**: Subscription status
- [ ] **Content**: Compliance alerts
- [ ] Verify "Admin" link in sidebar
- [ ] Navigate to `/admin` → Verify admin panel loads

### Test 3.6: Super Admin Dashboard
Login as: `super_admin@lockdev.test`

- [ ] Verify route: `/dashboard` or automatic redirect to `/super-admin`
- [ ] **Content**: Platform-wide metrics
- [ ] **Content**: Active organizations summary
- [ ] **Content**: System health indicators
- [ ] Verify sidebar shows "Super Admin" section
- [ ] Navigate to `/super-admin/organizations` → Verify org list
- [ ] Navigate to `/super-admin/users` → Verify user list
- [ ] Navigate to `/super-admin/system` → Verify system health page

---

## Section 4: Patient Management Verification

### Test 4.1: Patient List (`/patients`)
Login as: Provider or Staff

- [ ] Navigate to `/patients`
- [ ] Verify search input (name, MRN)
- [ ] Verify filter controls (status: Active, Discharged)
- [ ] Verify patient cards display: Name, DOB, MRN, Primary Provider
- [ ] Verify "Create Patient" button navigates to `/patients/new`
- [ ] **Pagination**: Verify pagination controls if many patients

### Test 4.2: Create Patient (`/patients/new`)
Login as: Provider, Staff, or Admin

- [ ] Navigate to `/patients/new`
- [ ] Verify form fields: First name, Last name, DOB, Legal sex, MRN
- [ ] Verify contact methods section (Type, Value, Is Primary, Safe for voicemail)
- [ ] Verify provider selector
- [ ] Submit valid data → Verify redirect to `/patients/:id`
- [ ] Verify validation errors on invalid data

### Test 4.3: Patient Detail (`/patients/:patientId`)
Login as: Provider or Staff

- [ ] Navigate to patient detail page
- [ ] Verify header: Patient name, photo, DOB, MRN
- [ ] Verify tabs: Overview, Documents, Care Team, Appointments, Messages
- [ ] **Overview tab**: Demographics, contact info
- [ ] **Documents tab**: Document list, upload area
- [ ] **Care Team tab**: List of assigned providers
- [ ] **Appointments tab**: Upcoming and past appointments
- [ ] **Messages tab**: Message threads for patient

### Test 4.4: Proxy Patient List (`/proxy/patients`)
Login as: Proxy

- [ ] Navigate to `/proxy/patients`
- [ ] Verify list of managed patients from `Patient_Proxy_Assignment`
- [ ] Verify patient card: photo, name, DOB
- [ ] Verify relationship type badge (Parent, Guardian, POA)
- [ ] Verify permission icons (clinical ✓, billing ✓, scheduling ✓)
- [ ] Click patient → Verify navigation to `/patients/:patientId`

---

## Section 5: Appointments Verification

### Test 5.1: Appointment List (`/appointments`)
Login as: Patient, Proxy, Provider, or Staff

- [ ] Navigate to `/appointments`
- [ ] **Patient/Proxy view**: Upcoming appointments cards, past collapsible
- [ ] **Provider view**: Today's schedule timeline
- [ ] **Staff view**: All org appointments with search/filter
- [ ] Verify "Schedule Appointment" button

### Test 5.2: Schedule Appointment (`/appointments/new`)
Login as: Patient, Proxy, Provider, or Staff

- [ ] Navigate to `/appointments/new`
- [ ] **Step 1** (Staff/Provider): Patient search/select
- [ ] **Step 2**: Provider list with availability indicators
- [ ] **Step 3**: Calendar date picker, available time slots
- [ ] **Step 4**: Appointment type (In-Person, Telehealth), reason
- [ ] **Step 5**: Confirmation summary
- [ ] Submit → Verify appointment created, redirect to detail

### Test 5.3: Appointment Detail (`/appointments/:appointmentId`)
- [ ] Navigate to appointment detail
- [ ] Verify header: date, time, status
- [ ] Verify patient and provider information
- [ ] Verify appointment type and reason
- [ ] Verify Cancel/Reschedule buttons
- [ ] Click "Reschedule" → Navigate to `/appointments/:id/reschedule`

### Test 5.4: Reschedule Appointment (`/appointments/:appointmentId/reschedule`)
- [ ] Verify current appointment summary displayed
- [ ] Verify provider availability calendar
- [ ] Select new time → Confirm → Verify update success

---

## Section 6: Messaging Verification

### Test 6.1: Message Inbox (`/messages`)
Login as: Any authenticated user

- [ ] Navigate to `/messages`
- [ ] Verify thread list sorted by most recent
- [ ] Verify unread count badge per thread
- [ ] Verify thread preview (participant names, last message snippet)
- [ ] Verify search input
- [ ] Verify filter tabs (All, Unread, Archived)

### Test 6.2: Compose Message (`/messages/new`)
- [ ] Navigate to `/messages/new`
- [ ] Verify recipient selector
- [ ] Verify subject line field
- [ ] Verify message body (rich text)
- [ ] Send message → Verify thread created, redirect to thread

### Test 6.3: Message Thread (`/messages/:threadId`)
- [ ] Navigate to message thread
- [ ] Verify thread header (subject, participants)
- [ ] Verify message list chronologically
- [ ] Verify reply composer at bottom
- [ ] Send reply → Verify appears in thread
- [ ] Verify real-time updates (SSE) if another user sends message

---

## Section 7: Admin Routes Verification

### Test 7.1: Admin Dashboard (`/admin`)
Login as: Organization Admin

- [ ] Navigate to `/admin`
- [ ] Verify organization overview stats
- [ ] Verify subscription status card
- [ ] Verify quick links to admin functions

### Test 7.2: Member Management (`/admin/members`)
- [ ] Navigate to `/admin/members`
- [ ] Verify member list with role badges
- [ ] Verify MFA status indicator
- [ ] Verify "Invite Member" button → `/admin/members/invite`
- [ ] Test: Change member role
- [ ] Test: Deactivate/remove member

### Test 7.3: Staff Management (`/admin/staff`)
- [ ] Navigate to `/admin/staff`
- [ ] Verify staff list with job titles
- [ ] Navigate to `/admin/staff/new`
- [ ] Verify staff profile creation form

### Test 7.4: Provider Management (`/admin/providers`)
- [ ] Navigate to `/admin/providers`
- [ ] Verify provider list with credentials
- [ ] Navigate to `/admin/providers/new`
- [ ] Verify NPI number input with validation
- [ ] Verify state licenses section

### Test 7.5: Audit Logs (`/compliance/audit-logs`)
Login as: Admin or Auditor

- [ ] Navigate to `/compliance/audit-logs`
- [ ] Verify filterable audit log table
- [ ] Verify columns: Timestamp, Actor, Action, Resource Type, IP Address
- [ ] Verify date range picker
- [ ] Verify export button (Admin only)

---

## Section 8: Super Admin Routes Verification

Login as: `super_admin@lockdev.test`

### Test 8.1: Super Admin Dashboard (`/super-admin`)
- [ ] Navigate to `/super-admin`
- [ ] Verify platform metrics (total organizations, users, patients)
- [ ] Verify system health summary
- [ ] Verify quick links

### Test 8.2: Organization Management (`/super-admin/organizations`)
- [ ] Navigate to `/super-admin/organizations`
- [ ] Verify organization list with: Name, ID, subscription status, member count
- [ ] Verify "Create Organization" button
- [ ] Test: Select organization → View details
- [ ] Test: Suspend/Delete organization (if implemented)

### Test 8.3: User Management (`/super-admin/users`)
- [ ] Navigate to `/super-admin/users`
- [ ] Verify user list: Email, display name, organizations, MFA status
- [ ] Verify search by email/name
- [ ] Verify filter by status (Active, Locked, Suspended)
- [ ] Test: Unlock locked account at `/super-admin/users/:id/unlock`

### Test 8.4: System Health (`/super-admin/system`)
- [ ] Navigate to `/super-admin/system`
- [ ] Verify service status cards (API, Database, Redis, S3)
- [ ] Verify metrics: request rate, error rate, job queue

---

## Section 9: Settings Verification

Login as: Any authenticated user

### Test 9.1: Settings Hub (`/settings`)
- [ ] Navigate to `/settings`
- [ ] Verify links: Profile, Security, Communication, Organizations
- [ ] Verify organization selector (if multi-org user)

### Test 9.2: Profile Settings (`/settings/profile`)
- [ ] Navigate to `/settings/profile`
- [ ] Verify display name field
- [ ] Verify profile photo upload
- [ ] Verify email (read-only)
- [ ] Update profile → Verify save success

### Test 9.3: Security Settings (`/settings/security`)
- [ ] Navigate to `/settings/security`
- [ ] Verify MFA status with setup/manage link
- [ ] Verify password change link
- [ ] Verify active sessions list
- [ ] Navigate to `/settings/security/password` → Verify password change form
- [ ] Navigate to `/settings/security/mfa` → Verify MFA setup/manage

### Test 9.4: Communication Preferences (`/settings/communication`)
- [ ] Navigate to `/settings/communication`
- [ ] Verify transactional communications toggle
- [ ] Verify marketing communications toggle
- [ ] Toggle settings → Verify auto-save

### Test 9.5: Timezone Settings
- [ ] Navigate to settings (profile or organization settings)
- [ ] Verify timezone selector component
- [ ] Select timezone → Verify save
- [ ] Verify times display in selected timezone

---

## Section 10: Notifications Verification

### Test 10.1: Notification History (`/notifications`)
- [ ] Navigate to `/notifications`
- [ ] Verify notification list (paginated)
- [ ] Verify Unread/All filter tabs
- [ ] Verify type filter (Appointments, Messages, System)
- [ ] Verify "Mark all as read" button
- [ ] Click notification → Verify navigation to source

### Test 10.2: Notification Panel (Slide-Out)
- [ ] Click notification bell in header
- [ ] Verify slide-out panel appears
- [ ] Verify recent notifications displayed
- [ ] Verify unread count badge on bell
- [ ] Click notification → Verify navigation and panel closes
- [ ] Click outside → Verify panel closes

### Test 10.3: Real-Time Notifications (SSE)
- [ ] Open two browser tabs as same user
- [ ] Trigger event (e.g., receive message) from another user
- [ ] Verify notification appears in real-time in both tabs

---

## Section 11: API Verification Checklist

For each major area, verify API endpoints are called correctly:

### Users & Authentication
- [ ] `GET /api/users/me` - Returns user profile and roles
- [ ] `PATCH /api/users/me` - Updates profile
- [ ] `GET /api/users/me/notifications` - Returns notifications

### Organizations
- [ ] `GET /api/organizations` - Lists user's organizations
- [ ] `GET /api/organizations/{org_id}` - Organization details

### Patients
- [ ] `GET /api/organizations/{org_id}/patients` - Patient list
- [ ] `POST /api/organizations/{org_id}/patients` - Create patient
- [ ] `GET /api/organizations/{org_id}/patients/{id}` - Patient detail
- [ ] `PATCH /api/organizations/{org_id}/patients/{id}` - Update patient

### Appointments
- [ ] `GET /api/organizations/{org_id}/appointments` - Appointment list
- [ ] `POST /api/organizations/{org_id}/appointments` - Create
- [ ] `PATCH /api/organizations/{org_id}/appointments/{id}` - Update

### Messaging
- [ ] `GET /api/organizations/{org_id}/messages` - Message threads
- [ ] `POST /api/organizations/{org_id}/messages` - Create thread
- [ ] `GET /api/organizations/{org_id}/messages/{id}` - Thread detail
- [ ] `POST /api/organizations/{org_id}/messages/{id}/replies` - Reply

### Health
- [ ] `GET /health` - Shallow health check
- [ ] `GET /health/deep` - Deep health check with DB/Redis

---

## Section 12: Error Handling Verification

### Test 12.1: 404 Page
- [ ] Navigate to non-existent route (e.g., `/nonexistent`)
- [ ] Verify 404 page displays
- [ ] Verify "Page not found" message
- [ ] Verify link to dashboard

### Test 12.2: 403 Page
- [ ] As Patient, try to access `/admin`
- [ ] Verify 403/Access Denied page
- [ ] Verify appropriate message

### Test 12.3: API Error Handling
- [ ] Trigger validation error → Verify inline form errors
- [ ] Simulate network error → Verify retry option

---

## Section 13: Accessibility Verification

### Test 13.1: Keyboard Navigation
- [ ] Tab through page → Verify all interactive elements focusable
- [ ] Verify visible focus rings on focused elements
- [ ] Press Escape on modals → Verify closes

### Test 13.2: Screen Reader Compatibility
- [ ] Verify semantic HTML structure (nav, main, headings)
- [ ] Verify ARIA labels on interactive elements
- [ ] Verify form error announcements

---

## Execution

1. Open `http://localhost:5173`
2. Test each section using dev login buttons
3. **Only document discrepancies** in `/docs/review/review-findings.md`
4. Categorize issues as P0/P1/P2
