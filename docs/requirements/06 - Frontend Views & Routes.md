# Frontend Views & Routes Reference

This document provides a comprehensive reference for all frontend views and routes in the Lockdev platform. Each route includes URL patterns, parameters, role restrictions, displayed content, and available actions.

> [!NOTE]
> This reference complements the [API Reference](./05%20-%20API%20Reference.md) and [Implementation Plan](./03%20-%20Implementation.md) documentation.

---

## Table of Contents

1. [Security & Session Management](#security--session-management)
2. [Route Overview](#route-overview)
3. [Public Routes](#public-routes)
4. [Authenticated Routes](#authenticated-routes)
   - [Onboarding Routes](#onboarding-routes)
   - [Dashboard](#dashboard)
   - [Patient & Proxy Routes](#patient--proxy-routes)
   - [Appointments](#appointments)
   - [Messaging](#messaging)
   - [Staff & Provider Routes](#staff--provider-routes)
   - [Call Center Routes](#call-center-routes)
   - [Admin Routes](#admin-routes)
   - [Compliance & Auditor Routes](#compliance--auditor-routes)
   - [Super Admin Routes](#super-admin-routes)
   - [Billing Routes](#billing-routes)
   - [Settings Routes](#settings-routes)
   - [Help Routes](#help-routes)
   - [Notification Routes](#notification-routes)
5. [Shared Components](#shared-components)
6. [UI States](#ui-states)
7. [Error Pages](#error-pages)
8. [API Error Handling](#api-error-handling)
9. [Accessibility](#accessibility)

---

## Security & Session Management

> [!CAUTION]
> This section documents HIPAA-required security controls. All implementations MUST follow these specifications.

### Session Timeout Policy

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Idle Timeout** | 15 minutes | HIPAA §164.312(a)(2)(iii) automatic logoff |
| **Warning Modal** | 2 minutes before expiry | User notification |
| **Absolute Timeout** | 12 hours | Maximum session length regardless of activity |
| **Remember Me** | Not available | PHI access requires fresh authentication |

**Implementation:**
- After 13 minutes of inactivity: Display warning modal with countdown
- After 15 minutes: Auto-logout, clear all state, redirect to `/login?reason=timeout`
- Activity = mouse move, keyboard input, touch, or API call

### MFA Requirements

| Role | MFA Required | Enforcement |
|------|--------------|-------------|
| Patient (Self-Managed) | Optional | Encouraged via banner |
| Proxy | Optional | Encouraged via banner |
| Provider | **Required** | Blocked from PHI routes until enabled |
| Clinical Staff | **Required** | Blocked from PHI routes until enabled |
| Administrative Staff | **Required** | Blocked from PHI routes until enabled |
| Call Center Agent | **Required** | Blocked from PHI routes until enabled |
| Organization Admin | **Required** | Blocked from all admin routes until enabled |
| Super Admin | **Required** | Blocked from all routes until enabled |
| Auditor | **Required** | Blocked from audit routes until enabled |

**Enforcement Flow:**
1. User logs in successfully
2. If role requires MFA and `mfa_enabled === false`:
   - Redirect to `/settings/security/mfa`
   - Display blocking modal: "MFA is required for your role"
   - Prevent navigation to any PHI-accessing route

### PHI Access Indicators

Routes accessing Protected Health Information (PHI) are marked with 🔒 throughout this document.

**PHI Routes Include:**
- `/patients/:patientId` and all sub-routes
- `/appointments/:appointmentId`
- `/messages/:threadId`
- `/call-center/patients/:patientId`
- `/admin/audit-logs` (contains patient identifiers)

### Break Glass (Impersonation) Requirements

> [!WARNING]
> Impersonation is a "Break Glass" action requiring mandatory audit logging.

**During Impersonation:**
- Persistent red banner at top of screen: "⚠️ Impersonating: [Patient Name] | Session ends in XX:XX | [End Session]"
- All actions logged with `impersonator_id` in audit trail
- Maximum duration: 1 hour (auto-expires)
- No access to: Admin routes, Settings changes, Billing modifications
- Visual distinction: Page border or watermark indicating impersonation mode

### Concurrent Session Policy

| Setting | Value |
|---------|-------|
| Max Active Sessions | 1 per user |
| New Login Behavior | Invalidates previous session |
| Notification | Previous session sees "Signed out: New session started elsewhere" |

### Account Lockout Policy

> [!CAUTION]
> Failed login lockout is required for HIPAA §164.312(d) person or entity authentication.

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Failed Attempts Threshold** | 5 consecutive failures | Prevent brute force attacks |
| **Initial Lockout Duration** | 15 minutes | Temporary lockout |
| **Progressive Lockout** | 30 min (6th-10th), 1 hour (11th+) | Escalating protection |
| **Lockout Scope** | Per-account, not per-IP | Prevents account enumeration |
| **Notification** | Email sent on lockout | Alert user of potential attack |
| **Admin Override** | Super Admin can unlock | Emergency access |

**Lockout UI States:**
- `/login?reason=locked&unlock_at=<timestamp>`: Display countdown to unlock
- `/login?reason=locked_permanent`: "Account locked. Contact support."

**Unlock Flow:**
1. Wait for lockout timer to expire → Account automatically unlocks
2. OR Use "Forgot Password" → Password reset clears lockout counter
3. OR Contact Support → Admin unlocks via `/super-admin/users/:userId/unlock`

### Password Change Session Invalidation

> [!NOTE]
> Per HIPAA §164.312(d), password changes invalidate all other active sessions.

**Behavior:**
- When password is changed via `/settings/security/password`:
  - All sessions except current are terminated
  - User is notified: "Password changed. All other sessions have been signed out."
  - Audit log entry created with all terminated session IDs

---

## Route Overview

### Quick Reference

| Route | Auth | MFA | Roles | PHI | Description |
|-------|------|-----|-------|-----|-------------|
| `/` | No | — | — | — | Landing page / Marketing |
| `/login` | No | — | — | — | User authentication |
| `/signup` | No | — | — | — | New user registration |
| `/forgot-password` | No | — | — | — | Password reset initiation |
| `/reset-password/:token` | No | — | — | — | Password reset completion |
| `/verify-email/:token` | No | — | — | — | Email verification |
| `/invite/:token` | No | — | — | — | Accept organization invite |
| `/consent` | Yes | No | All | — | Accept TOS/HIPAA |
| `/onboarding` | Yes | No | All | — | First-time user setup |
| `/dashboard` | Yes | Role | All | — | Role-based dashboard |
| `/patients` | Yes | Yes | Staff, Provider, Admin | 🔒 | Patient list |
| `/patients/new` | Yes | Yes | Staff, Provider, Admin | 🔒 | Create new patient |
| `/patients/:id` | Yes | Yes | Staff, Provider, Proxy, Patient | 🔒 | Patient detail |
| `/patients/:id/appointments` | Yes | Yes | Staff, Provider, Proxy, Patient | 🔒 | Patient appointments tab |
| `/patients/:id/messages` | Yes | Yes | Staff, Provider, Proxy, Patient | 🔒 | Patient messages tab |
| `/patients/:id/billing` | Yes | No | Patient, Proxy | — | Patient subscription |
| `/patients/:id/proxies` | Yes | Yes | Staff, Provider, Admin, Patient | 🔒 | Manage proxies |
| `/patients/:id/proxies/invite` | Yes | Yes | Staff, Provider, Admin | 🔒 | Invite proxy |
| `/appointments` | Yes | Role | Patient, Proxy, Provider, Staff | 🔒 | Appointment list |
| `/appointments/new` | Yes | Role | Patient, Proxy, Provider, Staff | 🔒 | Schedule appointment |
| `/appointments/:id` | Yes | Role | Patient, Proxy, Provider, Staff | 🔒 | Appointment detail |
| `/appointments/:id/reschedule` | Yes | Role | Patient, Proxy, Provider, Staff | 🔒 | Reschedule appointment |
| `/messages` | Yes | Role | All | 🔒 | Message inbox |
| `/messages/:threadId` | Yes | Role | All | 🔒 | Message thread |
| `/call-center` | Yes | Yes | Call Center Agent | 🔒 | Call center dashboard |
| `/settings` | Yes | No | All | — | User preferences |
| `/notifications` | Yes | No | All | — | Notification history |
| `/admin` | Yes | Yes | Admin, Super Admin | — | Admin panel |
| `/admin/staff/new` | Yes | Yes | Admin, Super Admin | — | Create staff profile |
| `/admin/providers/new` | Yes | Yes | Admin, Super Admin | — | Create provider profile |
| `/admin/billing` | Yes | Yes | Admin | — | Organization billing |
| `/admin/impersonate` | Yes | Yes | Admin, Super Admin | 🔒 | Patient impersonation |
| `/compliance` | Yes | Yes | Auditor, Admin, Super Admin | 🔒 | Compliance dashboard |
| `/super-admin` | Yes | Yes | Super Admin | — | Platform dashboard |
| `/super-admin/organizations` | Yes | Yes | Super Admin | — | Platform org management |
| `/super-admin/users` | Yes | Yes | Super Admin | 🔒 | Platform user management |
| `/super-admin/users/:id/unlock` | Yes | Yes | Super Admin | — | Unlock user account |
| `/super-admin/system` | Yes | Yes | Super Admin | — | System health |
| `/help` | Yes | No | All | — | Help center |

---

## Public Routes

### `/` — Landing Page

| Property | Value |
|----------|-------|
| **Auth Required** | No |
| **Roles** | — |
| **Purpose** | Marketing landing page with app overview and CTA |

**Content:**
- Hero section with value proposition
- Feature highlights
- Testimonials / trust indicators
- Call-to-action buttons (Login, Get Started)
- Links to `/legal/privacy` and `/legal/terms`

**Actions:**
- Navigate to `/login`
- Navigate to `/signup`

**States:**
- *Loading:* N/A (static content)
- *Error:* N/A

---

### `/login` — Sign In

| Property | Value |
|----------|-------|
| **Auth Required** | No |
| **Roles** | — |
| **Purpose** | Authenticate existing users |

**Content:**
- Email/password form
- Google Sign-In button (OAuth via GCIP)
- "Forgot Password" link
- "Create Account" link

**Actions:**
- Submit credentials → Redirect to `/dashboard` (or `/consent` if pending)
- Google OAuth flow
- Navigate to `/forgot-password`
- Navigate to `/signup`

**Query Parameters:**
| Parameter | Description |
|-----------|-------------|
| `redirect` | URL to redirect after successful login |
| `reason` | `timeout`, `logout`, `session_expired` — displays appropriate message |

**Redirects:**
- If already authenticated → `/dashboard`

**States:**
- *Loading:* Button spinner during auth
- *Error:* "Invalid credentials", "Account locked", "Too many attempts"

---

### `/signup` — Registration

| Property | Value |
|----------|-------|
| **Auth Required** | No |
| **Roles** | — |
| **Purpose** | Create new user account |

**Content:**
- Email/password registration form
- Google Sign-In option
- Terms checkbox (links to `/legal/terms`)
- Privacy policy link (links to `/legal/privacy`)

**Actions:**
- Submit registration → Redirect to `/verify-email`
- Google OAuth flow → Redirect to `/consent`

**Redirects:**
- If already authenticated → `/dashboard`

**States:**
- *Loading:* Button spinner during registration
- *Error:* "Email already registered", "Password too weak"

---

### `/forgot-password` — Password Reset Request

| Property | Value |
|----------|-------|
| **Auth Required** | No |
| **Roles** | — |
| **Purpose** | Initiate password reset flow |

**Content:**
- Email input form
- Confirmation message (shows regardless of email existence for security)

**Actions:**
- Submit email → Firebase sends reset email
- Navigate back to `/login`

**States:**
- *Loading:* Button spinner
- *Success:* "Check your email for reset instructions"
- *Error:* "Too many requests. Try again later."

---

### `/reset-password/:token` — Password Reset Completion

| Property | Value |
|----------|-------|
| **Auth Required** | No |
| **Roles** | — |
| **URL Parameters** | `token` (Firebase password reset token) |
| **Purpose** | Complete password reset flow |

**Content:**
- New password input
- Confirm password input
- Password strength indicator

**Actions:**
- Submit new password → Redirect to `/login?reason=password_reset`

**States:**
- *Loading:* Button spinner
- *Error:* "Token expired", "Token invalid", "Password too weak"

---

### `/verify-email/:token` — Email Verification

| Property | Value |
|----------|-------|
| **Auth Required** | No |
| **Roles** | — |
| **URL Parameters** | `token` (Firebase email verification token) |
| **Purpose** | Verify user email address |

**Content:**
- Loading spinner during verification
- Success/failure message
- Link to login

**Actions:**
- Auto-verify on load → Redirect to `/login` on success

**States:**
- *Loading:* Verification in progress
- *Success:* "Email verified! Redirecting to login..."
- *Error:* "Verification link expired", "Resend verification email" button

---

### `/invite/:token` — Accept Organization Invitation

| Property | Value |
|----------|-------|
| **Auth Required** | No (redirects to login/signup if needed) |
| **Roles** | — |
| **URL Parameters** | `token` (Invitation token) |
| **Purpose** | Accept invitation to join organization |

**Content:**
- Organization name and logo
- Role being offered
- Inviter name
- Accept/Decline buttons

**Flow:**
1. If not authenticated → Store token, redirect to `/login?redirect=/invite/:token`
2. If authenticated → Show acceptance form
3. On accept → Redirect to `/dashboard` with org context

**API Calls:**
- `GET /api/invitations/{token}` — Validate and get invite details
- `POST /api/invitations/{token}/accept` — Accept invitation

**States:**
- *Loading:* "Loading invitation..."
- *Error:* "Invitation expired", "Invitation already used"

---

### `/legal/privacy` — Privacy Policy

| Property | Value |
|----------|-------|
| **Auth Required** | No |
| **Purpose** | Display privacy policy |

**Content:**
- Full privacy policy text
- Last updated date
- Link back to home/login

---

### `/legal/terms` — Terms of Service

| Property | Value |
|----------|-------|
| **Auth Required** | No |
| **Purpose** | Display terms of service |

**Content:**
- Full terms of service text
- Last updated date
- Link back to home/login

---

## Authenticated Routes

> [!IMPORTANT]
> All authenticated routes require a valid Firebase/GCIP JWT token. Users without valid consent records are redirected to `/consent`.

### Onboarding Routes

#### `/consent` — Legal Consent

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **MFA Required** | No (consent happens before MFA setup) |
| **Purpose** | Capture required legal consents (TOS, HIPAA) |

**Content:**
- List of pending consent documents
- Document content viewer (scrollable)
- Signature checkbox per document
- Communication preferences (transactional/marketing)

**Actions:**
- Accept/reject each document
- Submit all consents → Proceed to `/onboarding` (first login) or `/dashboard`

**API Calls:**
- `GET /api/consent/required` — Get pending consent documents for user
- `GET /api/consent/documents/{document_id}/content` — Get document content
- `POST /api/consent` — Submit signed consents

> [!NOTE]
> See [API Reference - Consent & Compliance](./05%20-%20API%20Reference.md#consent--compliance) for complete endpoint documentation.

**Blocked Until:** All required documents signed

**States:**
- *Loading:* Skeleton document list
- *Empty:* N/A (redirects to dashboard if no pending)
- *Error:* "Failed to load consent documents. Retry" button

---

#### `/onboarding` — First-Time User Setup

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users (first login only) |
| **MFA Required** | No (MFA setup is step in onboarding) |
| **Purpose** | Guide new users through initial setup |

**Content (Multi-Step Wizard):**

**Step 1: Profile Setup**
- Display name
- Profile photo (optional)
- Phone number (for MFA)

**Step 2: MFA Setup** (Required for Staff/Provider/Admin roles)
- QR code for authenticator app
- Backup codes display (must acknowledge saving)
- Verification code input

**Step 3: Organization Context** (if multiple orgs)
- List organizations user belongs to
- Select default/active organization

**Step 4: Role-Specific Tutorial**
- Quick tour of relevant features
- Skip option available

**Actions:**
- Complete each step → Progress to next
- Skip optional steps → Mark as skipped
- Complete wizard → Navigate to `/dashboard`

**API Calls:**
- `PATCH /api/users/me` — Update profile
- `POST /api/users/me/mfa/setup` — Initialize MFA
- `POST /api/users/me/mfa/verify` — Verify MFA setup

**States:**
- *Loading:* Step content loading
- *Error:* "Setup failed. Retry" with option to skip

---

### Dashboard

#### `/dashboard` — Role-Based Dashboard

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **MFA Required** | Role-dependent (see MFA Requirements table) |
| **Purpose** | Primary landing page with role-specific content |

**Redirect Logic:**
1. If not authenticated → `/login`
2. If consent pending → `/consent`
3. If first login and onboarding incomplete → `/onboarding`
4. If MFA required but not enabled → `/settings/security/mfa`
5. Otherwise → Show dashboard

**Content by Role:**

**Patient Dashboard:**
- Upcoming appointments (next 3)
- Unread messages count with preview
- Care team quick contacts
- Subscription status banner (if past due)
- Health tips or educational content (non-PHI)

**Proxy Dashboard:**
- Quick access to managed patients (cards)
- Upcoming appointments across all patients
- Unread messages per patient
- Alert banners for expiring proxy access

**Provider Dashboard:**
- Today's appointments (timeline view)
- Unread messages count
- Pending tasks/follow-ups
- Patient panel overview (new/active counts)

**Clinical Staff Dashboard:**
- Task queue
- Today's patient schedule
- Pending approvals or reviews
- Quick patient search

**Administrative Staff Dashboard:**
- Appointment scheduling queue
- Pending patient registrations
- Billing alerts (overdue accounts)
- Recent activity feed

**Call Center Agent Dashboard:**
- Same as `/call-center` (redirects to `/call-center`)

**Organization Admin Dashboard:**
- Organization health metrics
- Member activity summary
- Subscription status
- Compliance alerts (unsigned consents, expired licenses)

**Super Admin Dashboard:**
- Platform-wide metrics
- Active organizations summary
- System health indicators
- Cross-organization audit summary

**API Calls:**
- `GET /api/users/me` — User profile and roles
- `GET /api/organizations/{org_id}/appointments?limit=5` — Upcoming appointments
- `GET /api/organizations/{org_id}/messages?filter=unread&limit=5` — Unread messages
- Role-specific additional calls (see above)

**States:**
- *Loading:* Skeleton dashboard with placeholders for each section
- *Empty:* Role-appropriate welcome message with quick-start CTAs
- *Error:* "Failed to load dashboard. Retry" button

**Breadcrumb:** None (root level)

---

### Patient & Proxy Routes

#### `/proxy/patients` — Proxy Patient List

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Proxy only |
| **MFA Required** | No (Recommended if `can_view_clinical_notes` granted) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View all patients managed by the proxy |

**Content:**
- List of managed patients (from `Patient_Proxy_Assignment`)
- Patient card with photo, name, DOB
- Relationship type badge (Parent, Guardian, POA)
- Permission summary icons (clinical ✓, billing ✓, scheduling ✓)
- Quick access buttons

**Actions:**
- Select patient → Navigate to `/patients/:patientId`
- View permission details → Modal with full permissions

**API Calls:**
- `GET /api/users/me/proxy/patients`

> [!NOTE]
> Legacy path `/api/proxies/me/patients` is supported for backwards compatibility.

**States:**
- *Loading:* Skeleton cards
- *Empty:* "No patients assigned to your account. Contact your healthcare provider to be added as a proxy." with help link
- *Error:* "Failed to load patients. Retry" button

---

#### `/patients` — Patient List (Staff View) 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Clinical Staff, Administrative Staff, Admin |
| **MFA Required** | Yes |
| **PHI Access** | 🔒 Yes |
| **Query Parameters** | `search`, `status`, `limit`, `offset` |
| **Purpose** | Search and browse patients in the organization |

**Content:**
- Search input (name, MRN)
- Filter controls (status: Active, Discharged)
- Paginated patient list with cards
- Quick view: Name, DOB, MRN, Primary Provider

**Actions:**
- Search/filter patients
- Navigate to patient detail
- Create new patient → Navigate to `/patients/new`

**API Calls:**
- `GET /api/organizations/{org_id}/patients`

**States:**
- *Loading:* Skeleton list
- *Empty:* "No patients found matching your criteria"
- *Error:* "Failed to load patients. Retry" button

---

#### `/patients/new` — Create Patient 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Clinical Staff, Administrative Staff, Admin |
| **MFA Required** | Yes |
| **PHI Access** | 🔒 Yes (creating PHI) |
| **Purpose** | Create a new patient record |

**Content:**
- Demographics form:
  - First name, Last name (required)
  - Date of birth (required)
  - Legal sex
  - Medical Record Number
- Contact methods:
  - Type (Mobile, Home, Email)
  - Value
  - Is Primary checkbox
  - Safe for voicemail checkbox
- Primary provider selector

**Actions:**
- Submit → Navigate to `/patients/:newPatientId`
- Cancel → Navigate to `/patients`

**API Calls:**
- `POST /api/organizations/{org_id}/patients`
- `GET /api/organizations/{org_id}/providers` — For provider selector

**States:**
- *Loading:* Submit button spinner
- *Error:* Inline validation errors, "Failed to create patient" toast

---

#### `/patients/:patientId` — Patient Detail 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Clinical Staff, Administrative Staff (limited), Proxy (assigned), Patient (self) |
| **MFA Required** | Yes (Staff/Provider) |
| **URL Parameters** | `patientId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View comprehensive patient information |

**Content:**
- **Header:** Patient name, photo, DOB, MRN
- **Tabs:**
  - Overview (demographics, contact info)
  - Documents
  - Care Team
  - Appointments
  - Messages

**Breadcrumb:** `Dashboard > Patients > [Patient Name]`

**Actions:**
- Edit demographics (Staff, Provider, Admin)
- Upload document
- View/download documents
- Message care team
- Schedule appointment

**Permission Matrix:**

| Action | Patient | Proxy* | Provider | Clinical Staff | Admin Staff | Admin |
|--------|---------|--------|----------|----------------|-------------|-------|
| View demographics | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Edit demographics | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| View clinical notes | ✓ | ✓** | ✓ | ✓ | ✗ | ✓ |
| Upload documents | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| View billing | ✓ | ✓** | ✗ | ✗ | ✓ | ✓ |
| Schedule appointments | ✓ | ✓** | ✓ | ✓ | ✓ | ✓ |

> *\* Proxy access depends on `permissions_mask` in `Patient_Proxy_Assignment`*
> *\*\* Requires specific permission flag (`can_view_clinical_notes`, `can_view_billing`, `can_schedule_appointments`)*

**API Calls:**
- `GET /api/organizations/{org_id}/patients/{patient_id}`
- `PATCH /api/organizations/{org_id}/patients/{patient_id}`

**States:**
- *Loading:* Skeleton layout with tabs
- *Error:* "Patient not found" or "Access denied"

---

#### `/patients/:patientId/documents` — Patient Documents 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Clinical Staff, Proxy (with `can_view_clinical_notes`), Patient (self) |
| **MFA Required** | Yes (Staff/Provider) |
| **URL Parameters** | `patientId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View and manage patient documents |

**Content:**
- Document list with metadata (type, date, uploader)
- Upload area (drag-and-drop)
- Virus scan status indicator (Pending, Clean, Infected)
- Processing status (for OCR)

**Actions:**
- Upload new document
- Download document (presigned URL)
- View document inline (PDF viewer)
- Delete document (Admin only)

**API Calls:**
- `GET /api/organizations/{org_id}/patients/{patient_id}/documents`
- `POST /api/organizations/{org_id}/documents/upload-url`
- `GET /api/organizations/{org_id}/documents/{document_id}/download-url`
- `DELETE /api/organizations/{org_id}/documents/{document_id}`

**States:**
- *Loading:* Skeleton document list
- *Empty:* "No documents yet. Upload the first document." with upload CTA
- *Error:* "Failed to load documents. Retry" button

---

#### `/patients/:patientId/care-team` — Care Team 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Staff, Proxy, Patient (self) |
| **MFA Required** | Yes (Staff/Provider) |
| **URL Parameters** | `patientId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View and manage the patient's care team |

**Content:**
- List of assigned providers (Primary, Specialist, Consultant)
- Provider cards with photo, name, specialty
- Primary provider badge

**Actions:**
- Add provider to care team (Admin, Primary Provider)
- Remove provider from care team
- Designate primary provider

**API Calls:**
- `GET /api/organizations/{org_id}/patients/{patient_id}/care-team`
- `POST /api/organizations/{org_id}/patients/{patient_id}/care-team`
- `DELETE /api/organizations/{org_id}/patients/{patient_id}/care-team/{assignment_id}`

**States:**
- *Loading:* Skeleton provider cards
- *Empty:* "No care team assigned yet."
- *Error:* "Failed to load care team. Retry" button

---

#### `/patients/:patientId/proxies` — Proxy Management 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Staff (Clinical/Admin), Admin, Patient (self) |
| **MFA Required** | Yes |
| **URL Parameters** | `patientId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | Manage proxy access for a patient (dependents workflow) |

> [!NOTE]
> This route enables the proxy assignment workflow, allowing providers/staff to grant caregivers access to patient information.

**Content:**
- List of assigned proxies with:
  - Proxy name and email
  - Relationship type badge (Parent, Guardian, POA, Spouse)
  - Permission summary (Clinical ✓, Billing ✓, Scheduling ✓)
  - Verification status (Verified, Pending, Expired)
  - Expiration date (if set)
- Add proxy button
- Pending invitations list

**Actions:**
- Add new proxy → `/patients/:patientId/proxies/invite`
- Edit proxy permissions → Modal
- Revoke proxy access
- View verification documents
- Resend invitation

**API Calls:**
- `GET /api/organizations/{org_id}/patients/{patient_id}/proxies`
- `DELETE /api/organizations/{org_id}/patients/{patient_id}/proxies/{assignment_id}`
- `PATCH /api/organizations/{org_id}/patients/{patient_id}/proxies/{assignment_id}`

**States:**
- *Loading:* Skeleton proxy cards
- *Empty:* "No proxies assigned. Add a caregiver to grant access to this patient's information." with "Add Proxy" CTA
- *Error:* "Failed to load proxies. Retry" button

---

#### `/patients/:patientId/proxies/invite` — Invite Proxy 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Staff (Clinical/Admin), Admin |
| **MFA Required** | Yes |
| **URL Parameters** | `patientId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | Invite a caregiver to become a proxy for a patient |

> [!IMPORTANT]
> Proxy invitations require careful verification, especially for Power of Attorney or Legal Guardian relationships.

**Content (Multi-Step):**

**Step 1: Proxy Information**
- Email address input
- First name, Last name
- Phone number (optional)

**Step 2: Relationship Type**
- Dropdown: Parent, Guardian, POA, Spouse, Other
- Relationship documentation upload (required for POA/Guardian)
  - Accepted: PDF, JPG, PNG
  - Status: Pending verification

**Step 3: Permissions**
- Checkboxes:
  - ☑ View clinical notes (`can_view_clinical_notes`)
  - ☑ View billing information (`can_view_billing`)
  - ☑ Schedule appointments (`can_schedule_appointments`)
  - ☑ Send messages on behalf of patient (`can_message`)
- Expiration date (optional) — for temporary access

**Step 4: Confirmation**
- Summary of proxy details and permissions
- Audit warning: "This action is logged for HIPAA compliance"
- Confirm/Edit buttons

**Actions:**
- Complete invitation → Send email to proxy → Navigate to `/patients/:patientId/proxies`
- Cancel → Navigate to `/patients/:patientId/proxies`

**API Calls:**
- `POST /api/organizations/{org_id}/patients/{patient_id}/proxies`
- `POST /api/organizations/{org_id}/documents/upload-url` — For relationship documentation

**States:**
- *Loading:* Step content loading
- *Error:* "Failed to send invitation. Email may already be associated with a proxy."

---

#### `/patients/:patientId/appointments` — Patient Appointments Tab 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Staff, Proxy (with `can_schedule_appointments`), Patient (self) |
| **MFA Required** | Yes (Staff/Provider) |
| **URL Parameters** | `patientId` (ULID) |
| **Query Parameters** | `status`, `start_date`, `end_date` |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View and manage appointments for a specific patient |

> [!NOTE]
> This is the "Appointments" tab within the patient detail view. The URL allows deep-linking directly to this tab.

**Content:**
- Upcoming appointments list
- Past appointments (collapsible)
- Schedule new appointment CTA

**Actions:**
- View appointment details → `/appointments/:appointmentId`
- Schedule new appointment → `/appointments/new?patient_id=:patientId`
- Cancel appointment
- Reschedule appointment

**API Calls:**
- `GET /api/organizations/{org_id}/patients/{patient_id}/appointments`
- `DELETE /api/organizations/{org_id}/appointments/{appointment_id}`

**Breadcrumb:** `Dashboard > Patients > [Patient Name] > Appointments`

**States:**
- *Loading:* Skeleton appointment cards
- *Empty:* "No appointments scheduled." with "Schedule Appointment" CTA
- *Error:* "Failed to load appointments. Retry" button

---

#### `/patients/:patientId/messages` — Patient Messages Tab 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Provider, Staff, Proxy, Patient (self) |
| **MFA Required** | Yes (Staff/Provider) |
| **URL Parameters** | `patientId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View message threads related to a specific patient |

> [!NOTE]
> This is the "Messages" tab within the patient detail view. Shows threads filtered by patient context.

**Content:**
- Message threads involving this patient
- Unread count per thread
- Last message preview

**Actions:**
- View thread → `/messages/:threadId`
- Compose new message → `/messages/new?patient_id=:patientId`

**API Calls:**
- `GET /api/organizations/{org_id}/messages?patient_id={patient_id}`

**Breadcrumb:** `Dashboard > Patients > [Patient Name] > Messages`

**States:**
- *Loading:* Skeleton message list
- *Empty:* "No messages for this patient." with "Start Conversation" CTA
- *Error:* "Failed to load messages. Retry" button

---

### Appointments

#### `/appointments` — Appointment List 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Patient, Proxy, Provider, Clinical Staff, Administrative Staff |
| **MFA Required** | Yes (Staff/Provider) |
| **Query Parameters** | `date`, `status`, `patient_id`, `provider_id`, `limit`, `offset` |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View and manage appointments |

**Content varies by role:**

**Patient/Proxy View:**
- Upcoming appointments (card list)
- Past appointments (collapsible)
- Calendar view toggle

**Provider View:**
- Today's schedule (timeline)
- Upcoming appointments
- Filter by date range

**Staff View:**
- All organization appointments
- Search by patient, provider
- Filter controls

**Actions:**
- Schedule new appointment → `/appointments/new`
- View appointment details → `/appointments/:id`
- Cancel appointment (with reason)
- Reschedule appointment

**API Calls:**
- `GET /api/organizations/{org_id}/appointments`
- `DELETE /api/organizations/{org_id}/appointments/{appointment_id}`

**States:**
- *Loading:* Skeleton appointment cards or calendar
- *Empty:* "No appointments scheduled." with "Schedule Now" CTA
- *Error:* "Failed to load appointments. Retry" button

---

#### `/appointments/new` — Schedule Appointment 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Patient, Proxy (with `can_schedule_appointments`), Provider, Clinical Staff, Administrative Staff |
| **MFA Required** | Yes (Staff/Provider) |
| **Query Parameters** | `patient_id` (optional, pre-selects patient) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | Schedule a new appointment |

**Content (Multi-Step):**

**Step 1: Select Patient** (Staff/Provider only)
- Patient search/select

**Step 2: Select Provider**
- Provider list with availability indicators
- Specialty filter

**Step 3: Select Date/Time**
- Calendar date picker
- Available time slots

**Step 4: Appointment Details**
- Appointment type (In-Person, Telehealth)
- Reason for visit (text)
- Notes (optional)

**Step 5: Confirmation**
- Summary of appointment
- Confirm/Edit buttons

**Actions:**
- Navigate between steps
- Confirm → Create appointment → Navigate to `/appointments/:id`
- Cancel → Navigate back to `/appointments`

**API Calls:**
- `GET /api/organizations/{org_id}/patients` — Patient search
- `GET /api/organizations/{org_id}/providers` — Provider list
- `GET /api/organizations/{org_id}/providers/{provider_id}/availability` — Time slots
- `POST /api/organizations/{org_id}/appointments`

**States:**
- *Loading:* Step content loading
- *Error:* "Time slot no longer available. Please select another."

---

#### `/appointments/:appointmentId` — Appointment Detail 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Patient (self), Proxy (assigned), Provider (assigned), Staff |
| **MFA Required** | Yes (Staff/Provider) |
| **URL Parameters** | `appointmentId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View and manage appointment details |

**Content:**
- Appointment header (date, time, status)
- Patient information
- Provider information
- Appointment type and reason
- Location/telehealth link
- Cancel/Reschedule options

**Actions:**
- Join telehealth (if applicable)
- Cancel appointment
- Reschedule → `/appointments/:id/reschedule`
- Add to calendar (ICS download)

**API Calls:**
- `GET /api/organizations/{org_id}/appointments/{appointment_id}`
- `PATCH /api/organizations/{org_id}/appointments/{appointment_id}`
- `DELETE /api/organizations/{org_id}/appointments/{appointment_id}`

**States:**
- *Loading:* Skeleton layout
- *Error:* "Appointment not found"

---

#### `/appointments/:appointmentId/reschedule` — Reschedule Appointment 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Patient (self), Proxy (assigned), Provider (assigned), Staff |
| **MFA Required** | Yes (Staff/Provider) |
| **URL Parameters** | `appointmentId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | Change the date/time of an existing appointment |

**Content:**
- Current appointment summary (date, time, provider)
- Provider availability calendar
- Available time slots
- Reason for rescheduling (optional)

**Actions:**
- Select new date/time → Confirm reschedule → Navigate to `/appointments/:appointmentId`
- Cancel → Navigate to `/appointments/:appointmentId`

**API Calls:**
- `GET /api/organizations/{org_id}/appointments/{appointment_id}` — Current appointment
- `GET /api/organizations/{org_id}/providers/{provider_id}/availability` — Available slots
- `PATCH /api/organizations/{org_id}/appointments/{appointment_id}` — Update scheduled time

**States:**
- *Loading:* Calendar skeleton
- *Error:* "Appointment could not be rescheduled. The selected time may no longer be available."

---

### Messaging

#### `/messages` — Message Inbox 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **MFA Required** | Yes (Staff/Provider) |
| **Query Parameters** | `filter` (unread, archived), `search` |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View message threads |

**Content:**
- Thread list (sorted by most recent)
- Unread count badge
- Thread preview (participant names, last message snippet)
- Search input
- Filter tabs (All, Unread, Archived)

**Actions:**
- Select thread → `/messages/:threadId`
- Compose new message → `/messages/new`
- Archive thread
- Mark as read/unread

**API Calls:**
- `GET /api/organizations/{org_id}/messages`
- `PATCH /api/organizations/{org_id}/messages/{thread_id}` — Archive/read status

**States:**
- *Loading:* Skeleton thread list
- *Empty:* "No messages yet. Start a conversation with your care team." with compose CTA
- *Error:* "Failed to load messages. Retry" button

---

#### `/messages/new` — Compose Message 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **MFA Required** | Yes (Staff/Provider) |
| **Query Parameters** | `to` (optional, pre-selects recipient), `patient_id` (optional, context) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | Start a new message thread |

**Content:**
- Recipient selector (care team members, patient)
- Subject line
- Message body (rich text)
- Attachment option

**Actions:**
- Send → Create thread → Navigate to `/messages/:newThreadId`
- Cancel → Navigate to `/messages`

**API Calls:**
- `GET /api/organizations/{org_id}/members` — Recipient options (filtered by care team if `patient_id` provided)
- `GET /api/organizations/{org_id}/patients/{patient_id}/care-team` — Care team recipients (if patient context)
- `POST /api/organizations/{org_id}/messages`

**States:**
- *Loading:* Recipient list loading
- *Error:* "Failed to send message. Retry" button

---

#### `/messages/:threadId` — Message Thread 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Thread participants only |
| **MFA Required** | Yes (Staff/Provider) |
| **URL Parameters** | `threadId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View and reply to message thread |

**Content:**
- Thread header (subject, participants)
- Message list (chronological)
- Reply composer at bottom
- Attachment viewer

**Actions:**
- Send reply
- Attach file
- Archive thread
- Print thread

**API Calls:**
- `GET /api/organizations/{org_id}/messages/{thread_id}`
- `POST /api/organizations/{org_id}/messages/{thread_id}/replies`

**Real-Time:**
- SSE subscription for `message.new` events in this thread

**States:**
- *Loading:* Skeleton messages
- *Error:* "Thread not found" or "Access denied"

---

### Staff & Provider Routes

#### `/providers` — Provider Directory

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All organization members |
| **MFA Required** | No |
| **Query Parameters** | `specialty`, `search`, `limit`, `offset` |
| **Purpose** | View organization's provider directory |

**Content:**
- Provider list with specialty, NPI
- Contact information
- Search input
- Filter by specialty dropdown

**Actions:**
- View provider detail → `/providers/:providerId`
- Filter by specialty

**API Calls:**
- `GET /api/organizations/{org_id}/providers`

**States:**
- *Loading:* Skeleton provider cards
- *Empty:* "No providers found"
- *Error:* "Failed to load providers. Retry" button

---

#### `/providers/:providerId` — Provider Detail

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All organization members |
| **URL Parameters** | `providerId` (ULID) |
| **Purpose** | View provider profile |

**Content:**
- Provider photo, name, specialty
- NPI, DEA numbers (Admin only)
- State licenses with expiry dates
- Contact information
- Assigned patients list (Provider/Admin only)

**Actions:**
- (Admin) Edit provider information → Modal or inline
- View assigned patients
- Message provider

**API Calls:**
- `GET /api/organizations/{org_id}/providers/{provider_id}`
- `PATCH /api/organizations/{org_id}/providers/{provider_id}` — Update (Admin)

**States:**
- *Loading:* Skeleton profile
- *Error:* "Provider not found"

---

### Call Center Routes

#### `/call-center` — Call Center Dashboard 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Call Center Agent |
| **MFA Required** | Yes |
| **PHI Access** | 🔒 Yes |
| **Purpose** | Call center agent workspace |

**Content:**
- **Active Call Panel:** Current call information (if connected)
- **Queue Panel:** Incoming calls waiting
- **Recent Calls:** Last 20 calls handled
- **Quick Patient Search:** Search by name, DOB, phone
- **Task Queue:** Assigned follow-up tasks

**Actions:**
- Accept call from queue
- Search for patient
- Log call outcome
- Create follow-up task
- Transfer call

**API Calls:**
- `GET /api/call-center/queue`
- `GET /api/call-center/calls/recent`
- `GET /api/organizations/{org_id}/patients?search=...`

**Real-Time:**
- SSE subscription for `call.incoming`, `call.completed` events

**States:**
- *Loading:* Skeleton dashboard
- *Empty:* "No calls in queue. No tasks pending."

---

#### `/call-center/calls/:callId` — Call Detail 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Call Center Agent, Admin |
| **MFA Required** | Yes |
| **URL Parameters** | `callId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | View call record and outcome |

**Content:**
- Call metadata (date, duration, caller ID)
- Patient information (if identified)
- Call notes/outcome
- Recording link (if available, with audit)
- Follow-up tasks created

**Actions:**
- Edit call notes
- Create follow-up task
- Link to different patient

**API Calls:**
- `GET /api/call-center/calls/{call_id}`
- `PATCH /api/call-center/calls/{call_id}`

---

#### `/call-center/patients/:patientId` — Quick Patient View 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Call Center Agent |
| **MFA Required** | Yes |
| **URL Parameters** | `patientId` (ULID) |
| **PHI Access** | 🔒 Yes |
| **Purpose** | Streamlined patient view for call context |

**Content:**
- Patient demographics (name, DOB, phone)
- Upcoming appointments
- Recent call history with this patient
- Care team contacts
- Quick notes

**Actions:**
- Schedule appointment
- Send message to care team
- Transfer call
- Create follow-up task

**API Calls:**
- `GET /api/organizations/{org_id}/patients/{patient_id}`
- `GET /api/organizations/{org_id}/patients/{patient_id}/appointments?limit=5`
- `GET /api/call-center/patients/{patient_id}/call-history`

---

### Admin Routes

#### `/admin` — Admin Dashboard

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **Purpose** | Organization administration hub |

**Content:**
- Organization overview stats (members, patients, appointments)
- Subscription status card
- Recent activity summary
- Quick links to admin functions

**Actions:**
- Navigate to member management
- Navigate to audit logs
- Navigate to settings
- Navigate to billing

---

#### `/admin/members` — Member Management

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **Query Parameters** | `role`, `search`, `status`, `limit`, `offset` |
| **Purpose** | Manage organization members |

**Content:**
- Member list (Users with `Organization_Member` records)
- Role badges
- MFA status indicator
- Invitation status (Pending, Accepted)
- Last active timestamp

**Actions:**
- Invite new member → `/admin/members/invite`
- Change member role
- Deactivate member
- Remove member
- Resend invitation

**API Calls:**
- `GET /api/organizations/{org_id}/members`
- `PATCH /api/organizations/{org_id}/members/{member_id}`
- `DELETE /api/organizations/{org_id}/members/{member_id}`

---

#### `/admin/members/invite` — Invite Member

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **Purpose** | Send invitation to new organization member |

**Content:**
- Email input
- Role selector (Admin, Provider, Staff)
- Staff type selector (if Staff role: Clinical, Administrative, Call Center)
- Custom message (optional)

**Actions:**
- Send invitation → Returns to `/admin/members`
- Cancel → Navigate to `/admin/members`

**API Calls:**
- `POST /api/organizations/{org_id}/members`

---

#### `/admin/staff` — Staff Management

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **Query Parameters** | `job_title`, `search`, `limit`, `offset` |
| **Purpose** | Manage staff profiles and details |

**Content:**
- Staff list with job titles
- Employee ID
- Department/function

**Actions:**
- Create staff profile → `/admin/staff/new`
- Edit staff profile → Modal
- View staff member → `/admin/staff/:staffId`

**API Calls:**
- `GET /api/organizations/{org_id}/staff`
- `POST /api/organizations/{org_id}/staff`
- `PATCH /api/organizations/{org_id}/staff/{staff_id}`

---

#### `/admin/staff/new` — Create Staff Profile

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **Purpose** | Create a new staff profile for an existing member |

**Content:**
- Member selector (users without staff profiles)
- Employee ID input
- Job title selector (Clinical, Administrative, Call Center Agent)
- Department (optional)

**Actions:**
- Create → Navigate to `/admin/staff/:newStaffId`
- Cancel → Navigate to `/admin/staff`

**API Calls:**
- `GET /api/organizations/{org_id}/members?role=STAFF` — Available members
- `POST /api/organizations/{org_id}/staff`

**States:**
- *Loading:* Member list loading
- *Error:* "Failed to create staff profile. User may already have a profile."

---

#### `/admin/providers` — Provider Management

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **Purpose** | Manage provider credentials and licenses |

**Content:**
- Provider list with credentials
- License expiry warnings
- NPI validation status

**Actions:**
- Create provider profile → `/admin/providers/new`
- Edit provider credentials → Modal
- View license expirations

**API Calls:**
- `GET /api/organizations/{org_id}/providers`
- `POST /api/organizations/{org_id}/providers`
- `PATCH /api/organizations/{org_id}/providers/{provider_id}`

---

#### `/admin/providers/new` — Create Provider Profile

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **Purpose** | Create a new provider profile with credentials |

**Content:**
- Member selector (users without provider profiles)
- NPI Number input (with validation)
- DEA Number input (optional)
- Specialty selector
- State licenses section:
  - State dropdown
  - License number
  - Expiration date
  - Add/remove licenses

**Actions:**
- Create → Navigate to `/admin/providers/:newProviderId`
- Cancel → Navigate to `/admin/providers`

**API Calls:**
- `GET /api/organizations/{org_id}/members?role=PROVIDER` — Available members
- `POST /api/organizations/{org_id}/providers`

**States:**
- *Loading:* Member list loading
- *Error:* "Invalid NPI number", "Failed to create provider profile"

---

#### `/admin/impersonate` — Patient Impersonation 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **PHI Access** | 🔒 Yes (Break Glass) |
| **Purpose** | Impersonate patient for support |

> [!WARNING]
> This is a "Break Glass" action. All impersonation actions are logged with a mandatory reason.

**Content:**
- Patient search/select
- Reason input (required, minimum 10 characters)
- Confirmation dialog with audit warning
- Recent impersonation history (last 10)

**Impersonation Banner (During Active Session):**
```
┌──────────────────────────────────────────────────────────────────┐
│ ⚠️ IMPERSONATING: John Doe (MRN: 12345) | Expires in 58:32 | [End Session] │
└──────────────────────────────────────────────────────────────────┘
```

**Actions:**
- Search for patient
- Enter reason for impersonation (required)
- Confirm → Generate impersonation token → View as patient
- End session → Return to admin context

**API Calls:**
- `GET /api/organizations/{org_id}/patients?search=...`
- `POST /api/admin/impersonate/{patient_id}`

**Restrictions During Impersonation:**
- ✗ Cannot access `/admin` routes
- ✗ Cannot modify billing
- ✗ Cannot change settings
- ✗ Cannot impersonate another user
- ✓ Can view patient-facing pages only

**Session Management Implementation:**

> [!IMPORTANT]
> Impersonation requires careful session handling to maintain security and audit integrity.

**Token Storage:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Zustand Store: useImpersonationStore                            │
├─────────────────────────────────────────────────────────────────┤
│ originalToken: string | null    // Admin's Firebase token       │
│ impersonationToken: string      // Custom token with claims     │
│ patientId: string               // Being impersonated           │
│ patientName: string             // Display name for banner      │
│ reason: string                  // Audit reason                 │
│ expiresAt: Date                 // 1 hour max                   │
│ startedAt: Date                 // For countdown timer          │
└─────────────────────────────────────────────────────────────────┘
```

**Session Flow:**
1. **Start Impersonation:**
   - Store current admin token in `originalToken`
   - Call `POST /api/admin/impersonate/{patient_id}` with `{ reason: "..." }`
   - Receive custom token with claims: `{ act_as: patient_id, impersonator_id: admin_id }`
   - Store impersonation token, swap to use it for API calls
   - Display impersonation banner globally
   - Start countdown timer

2. **During Impersonation:**
   - All API calls use impersonation token (Axios interceptor)
   - Route guards check for impersonation state and block restricted routes
   - Banner remains sticky at top of all pages
   - Activity extends session but max 1 hour absolute

3. **End Impersonation (Manual or Timeout):**
   - Clear impersonation store
   - Restore `originalToken` for API calls
   - Log end-of-session audit event
   - Redirect to `/admin/impersonate`
   - Show confirmation: "Impersonation session ended"

**Security Notes:**
- Impersonation tokens are NOT persisted to localStorage (memory only)
- Browser refresh during impersonation ends the session (security feature)
- All actions during impersonation include `impersonator_id` in audit logs
- 5-minute warning before expiry with extend option

---

### Compliance & Auditor Routes

#### `/compliance` — Compliance Dashboard 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Auditor, Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **PHI Access** | 🔒 Masked by default |
| **Purpose** | Compliance oversight and audit access |

**Content:**
- Compliance score summary
- Recent audit activity (masked patient names)
- Pending consent reviews
- Quick links to audit logs, reports

**Actions:**
- Navigate to audit logs
- Generate compliance reports
- Review consent status

---

#### `/compliance/audit-logs` — Audit Log Viewer 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Auditor, Organization Admin, Super Admin |
| **MFA Required** | Yes |
| **Query Parameters** | `actor_user_id`, `resource_type`, `action_type`, `start_date`, `end_date`, `limit` |
| **PHI Access** | 🔒 Patient names masked for Auditor; visible for Admin with Break Glass |
| **Purpose** | View and search audit logs for compliance |

**Content:**
- Filterable audit log table
- Columns: Timestamp, Actor, Action, Resource Type, Resource ID, IP Address
- Date range picker
- Export button (CSV)

**For Auditor Role:**
- Patient names displayed as `Patient #XXXX` (last 4 of ULID)
- Break Glass option to reveal: triggers additional audit log entry

**Actions:**
- Filter by actor, resource type, action
- Date range filtering
- Export to CSV (Admin only)
- Break Glass to reveal PHI (logged)

**API Calls:**
- `GET /api/admin/audit-logs`
- `GET /api/admin/audit-logs/export`

**States:**
- *Loading:* Skeleton table
- *Empty:* "No audit logs match your criteria"
- *Error:* "Failed to load audit logs. Retry" button

---

### Super Admin Routes

> [!WARNING]
> Super Admin routes provide platform-wide access across all organizations. These actions are heavily audited and require MFA.

#### `/super-admin` — Super Admin Dashboard

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Super Admin only |
| **MFA Required** | Yes |
| **Purpose** | Platform-wide administration dashboard |

**Content:**
- Platform metrics (total organizations, users, patients)
- System health summary (API latency, error rates)
- Recent cross-organization activity
- Active impersonation sessions (all admins)
- Quick links to platform functions

**Actions:**
- Navigate to organization management
- Navigate to user management
- Navigate to system health
- View platform audit logs

---

#### `/super-admin/organizations` — Platform Organization Management

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Super Admin only |
| **MFA Required** | Yes |
| **Purpose** | Manage all organizations on the platform |

**Content:**
- Organization list with:
  - Name, ID, creation date
  - Subscription status badge
  - Member count
  - Patient count
  - Last activity
- Search and filter controls
- Create new organization button

**Actions:**
- Select organization → `/super-admin/organizations/:orgId`
- Create organization → `/super-admin/organizations/new`
- Suspend organization
- Delete organization (soft delete)

**API Calls:**
- `GET /api/super-admin/organizations`
- `POST /api/super-admin/organizations`
- `PATCH /api/super-admin/organizations/{org_id}`
- `DELETE /api/super-admin/organizations/{org_id}`

**States:**
- *Loading:* Skeleton table
- *Empty:* "No organizations on platform"
- *Error:* "Failed to load organizations. Retry" button

---

#### `/super-admin/users` — Platform User Management 🔒

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Super Admin only |
| **MFA Required** | Yes |
| **PHI Access** | 🔒 User emails and names |
| **Purpose** | Manage all users across all organizations |

**Content:**
- User list with:
  - Email, display name
  - Organizations (multi-org badge)
  - MFA status
  - Account status (Active, Locked, Suspended)
  - Last login
- Search by email/name
- Filter by status

**Actions:**
- View user details → `/super-admin/users/:userId`
- Unlock account
- Suspend account
- Force password reset
- Impersonate user (requires Break Glass)

**API Calls:**
- `GET /api/super-admin/users`
- `PATCH /api/super-admin/users/{user_id}`
- `POST /api/super-admin/users/{user_id}/unlock`
- `POST /api/super-admin/users/{user_id}/suspend`
- `POST /api/super-admin/users/{user_id}/force-password-reset`

**States:**
- *Loading:* Skeleton table
- *Empty:* "No users match search criteria"
- *Error:* "Failed to load users. Retry" button

---

#### `/super-admin/users/:userId/unlock` — Unlock User Account

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Super Admin only |
| **MFA Required** | Yes |
| **URL Parameters** | `userId` (ULID) |
| **Purpose** | Unlock a locked user account (failed login lockout) |

**Content:**
- User information summary
- Lockout reason (failed attempts count)
- Lockout timestamp
- Reason for unlock input (required)

**Actions:**
- Unlock account → Returns to `/super-admin/users`
- Cancel → Navigate to `/super-admin/users`

**API Calls:**
- `GET /api/super-admin/users/{user_id}`
- `POST /api/super-admin/users/{user_id}/unlock`

**States:**
- *Loading:* Content loading
- *Error:* "Account not locked" or "Failed to unlock account"

---

#### `/super-admin/system` — System Health

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Super Admin only |
| **MFA Required** | Yes |
| **Purpose** | Monitor platform health and performance |

**Content:**
- Real-time metrics dashboard:
  - API request rate (requests/minute)
  - Error rate (5xx/4xx percentages)
  - Database connection pool usage
  - Redis cache hit rate
  - Background job queue depth
- Service status cards (API, Database, Redis, S3, SES)
- Recent error log summary (no PHI)

**Actions:**
- Refresh metrics
- View detailed service logs
- Trigger manual health check

**API Calls:**
- `GET /api/super-admin/system/health`
- `GET /api/super-admin/system/metrics`

---

### Billing Routes

#### `/admin/billing` — Organization Billing

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Organization Admin |
| **MFA Required** | Yes |
| **Purpose** | Manage the organization's platform subscription |

**Content:**
- Current subscription status (Active, Past Due, Canceled)
- Plan details (name, price, billing period)
- Next billing date
- Payment method summary
- Invoice history link

**Actions:**
- Start subscription → Redirect to Stripe Checkout
- Manage billing → Redirect to Stripe Customer Portal
- Update payment method → Stripe Portal

**API Calls:**
- `GET /api/organizations/{org_id}`
- `POST /api/organizations/{org_id}/billing/checkout`
- `POST /api/organizations/{org_id}/billing/portal`

---

#### `/patients/:patientId/billing` — Patient Billing

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Patient (self), Proxy (with `can_view_billing`) |
| **MFA Required** | No |
| **URL Parameters** | `patientId` (ULID) |
| **Purpose** | Manage individual patient subscription |

**Content:**
- Subscription status for the specific patient
- Next billing date
- Payment method summary
- Invoice history

**Actions:**
- Subscribe patient → Redirect to Stripe Checkout
- Manage subscription → Redirect to Stripe Customer Portal

**API Calls:**
- `GET /api/organizations/{org_id}/patients/{patient_id}`
- `POST /api/organizations/{org_id}/patients/{patient_id}/billing/checkout`
- `POST /api/organizations/{org_id}/patients/{patient_id}/billing/portal`

---

### Settings Routes

#### `/settings` — User Settings Hub

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **MFA Required** | No |
| **Purpose** | User personal settings |

**Content:**
- Profile section link
- Security section link
- Communication preferences link
- Organization selector (if multi-org)

**Sub-Routes:**
- `/settings/profile` — Profile settings
- `/settings/security` — Security settings
- `/settings/security/password` — Change password
- `/settings/security/mfa` — MFA setup/management
- `/settings/communication` — Communication preferences
- `/settings/organizations` — Organization switcher
- `/settings/account` — Account management (delete, export)

---

#### `/settings/profile` — Profile Settings

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **Purpose** | Update user profile |

**Content:**
- Display name
- Profile photo
- Phone number
- Email (read-only, shows verified status)

**Actions:**
- Update profile → Save
- Change photo → Upload modal

**API Calls:**
- `GET /api/users/me`
- `PATCH /api/users/me`

---

#### `/settings/security` — Security Settings

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **Purpose** | Security settings overview |

**Content:**
- MFA status (Enabled/Disabled) with setup/manage link
- Password change link
- Active sessions list
- Recent login activity

**Actions:**
- Enable/Manage MFA → `/settings/security/mfa`
- Change password → `/settings/security/password`
- Terminate other sessions

**API Calls:**
- `GET /api/users/me`
- `GET /api/users/me/sessions`
- `DELETE /api/users/me/sessions/{session_id}`

---

#### `/settings/security/password` — Change Password

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **Purpose** | Change account password |

**Content:**
- Current password input
- New password input
- Confirm new password input
- Password strength indicator

**Actions:**
- Submit → Change password via Firebase
- Cancel → Back to `/settings/security`

**States:**
- *Loading:* Submit button spinner
- *Success:* "Password changed successfully" → Redirect to `/settings/security`
- *Error:* "Current password incorrect", "Password too weak"

---

#### `/settings/security/mfa` — MFA Setup & Management

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **Purpose** | Enable, disable, or manage MFA |

**Content (Setup Mode - MFA not enabled):**
- Step 1: Display QR code for authenticator app
- Step 2: Show backup codes (must acknowledge saving)
- Step 3: Enter verification code to confirm

**Content (Manage Mode - MFA enabled):**
- MFA status: Enabled ✓
- Regenerate backup codes option
- Disable MFA option (requires password confirmation)

**Actions:**
- Complete setup → Enable MFA
- Regenerate backup codes → Show new codes
- Disable MFA → Confirm with password

**API Calls:**
- `POST /api/users/me/mfa/setup`
- `POST /api/users/me/mfa/verify`
- `POST /api/users/me/mfa/backup-codes`
- `DELETE /api/users/me/mfa`

---

#### `/settings/communication` — Communication Preferences

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **Purpose** | Manage communication opt-ins (TCPA compliance) |

**Content:**
- Transactional communications toggle (appointments, billing)
- Marketing communications toggle
- Contact method preferences (Email, SMS, Push)
- Quiet hours setting

**Actions:**
- Toggle consents → Auto-save
- Set preferred contact method

**API Calls:**
- `GET /api/users/me/communication-preferences`
- `PATCH /api/users/me/communication-preferences`

---

#### `/settings/organizations` — Organization Selector

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | Users with multiple organization memberships |
| **Purpose** | Switch between organizations |

**Content:**
- List of user's organizations
- Current active organization indicator ✓
- Role per organization badge

**Actions:**
- Select organization → Switch context, redirect to `/dashboard`

**API Calls:**
- `GET /api/organizations`

---

#### `/settings/account` — Account Management

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **Purpose** | Account-level actions |

**Content:**
- Export my data section (HIPAA right of access)
- Delete account section

**Actions:**
- Request data export → Initiates background job, emails when ready
- Delete account → Confirmation modal with password → Soft delete

**API Calls:**
- `POST /api/users/me/export`
- `DELETE /api/users/me`

---

### Help Routes

#### `/help` — Help Center

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **Purpose** | Self-service help and support |

**Content:**
- Search help articles
- FAQ categories
- Contact support link
- Video tutorials (role-specific)

**Sub-Routes:**
- `/help/faq` — Frequently asked questions
- `/help/contact` — Contact support form

---

#### `/help/contact` — Contact Support

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **Purpose** | Submit support request |

**Content:**
- Category selector (Technical, Billing, Clinical, Other)
- Subject line
- Message body
- Screenshot attachment option
- Urgency selector

**Actions:**
- Submit → Create support ticket
- Attach screenshot

**API Calls:**
- `POST /api/support/tickets`

> [!NOTE]
> This endpoint may require addition to the API Reference as a future enhancement.

---

### Notification Routes

#### `/notifications` — Notification History

| Property | Value |
|----------|-------|
| **Auth Required** | Yes |
| **Roles** | All authenticated users |
| **MFA Required** | No |
| **Query Parameters** | `filter` (unread, all), `type` (appointment, message, system), `limit`, `offset` |
| **Purpose** | View all notifications and manage preferences |

**Content:**
- Notification list (paginated)
- Unread/All filter tabs
- Type filter (Appointments, Messages, System)
- Mark all as read button
- Per-notification read/unread toggle

**Notification Types:**
| Type | Events |
|------|--------|
| `appointment` | Scheduled, Rescheduled, Cancelled, Reminder |
| `message` | New message in thread |
| `care_team` | Provider assigned/removed |
| `billing` | Payment due, Payment received, Subscription change |
| `system` | Consent required, MFA reminder, Account security |
| `admin` | Member joined, License expiring (Admin only) |

**Actions:**
- Mark as read/unread
- Mark all as read
- Navigate to source (e.g., appointment detail)
- Delete notification (removes from list, not database)

**API Calls:**
- `GET /api/users/me/notifications`
- `PATCH /api/users/me/notifications/{notification_id}` — Mark read/unread
- `POST /api/users/me/notifications/mark-all-read`

**Real-Time:**
- SSE subscription for `notification.new` events
- Badge count updates automatically

**States:**
- *Loading:* Skeleton notification list
- *Empty:* "All caught up! No new notifications."
- *Error:* "Failed to load notifications. Retry" button

---

#### Notification Panel (Slide-Out)

> [!NOTE]
> The notification panel is accessible from the bell icon in the navigation header. It is not a separate route but a slide-out component available on all authenticated pages.

**Trigger:** Click notification bell in header

**Content:**
- Recent notifications (last 10)
- Unread count badge on bell icon
- Quick actions per notification
- "View All" link → `/notifications`

**Behavior:**
- Opens as right-side slide-out panel
- Click outside to close
- Clicking a notification navigates to source and closes panel
- Real-time updates via SSE

---

## Shared Components

### Navigation Header
- Logo (links to `/dashboard`)
- Organization selector (if multi-org) — dropdown
- Search bar (global patient search for Staff/Provider)
- Notification bell (links to notification panel)
- User menu (profile, settings, logout)
- **SSE Status Indicator:** Green dot = connected, Yellow = reconnecting, Red = offline

### Sidebar Navigation

| Item | Roles | Route |
|------|-------|-------|
| Dashboard | All | `/dashboard` |
| My Patients | Proxy | `/proxy/patients` |
| Patients | Staff, Provider, Admin | `/patients` |
| Appointments | Patient, Proxy, Staff, Provider | `/appointments` |
| Messages | All | `/messages` |
| Call Center | Call Center Agent | `/call-center` |
| Providers | All | `/providers` |
| Settings | All | `/settings` |
| Admin | Admin, Super Admin | `/admin` |
| Compliance | Auditor, Admin | `/compliance` |
| Help | All | `/help` |

### Consent Banner
- Displayed when new consent documents require signature
- Blocks navigation to PHI routes until addressed
- Links to `/consent`
- Dismissible only by completing consent

### Session Warning Modal
Appears 2 minutes before session expiry:
```
┌─────────────────────────────────────────┐
│ ⏰ Session Expiring                      │
│                                         │
│ Your session will expire in 1:58        │
│                                         │
│ [Stay Signed In]    [Sign Out Now]      │
└─────────────────────────────────────────┘
```

### Impersonation Banner
Displayed during Break Glass sessions (see `/admin/impersonate`).

---

## UI States

Each route should implement these standard states:

### Loading State
- Skeleton loaders matching the content structure
- Shimmer animation
- Preserve layout to prevent layout shift

### Empty State
- Friendly illustration
- Clear message explaining emptiness
- Primary action CTA when applicable
- Example: "No patients found. Try adjusting your search."

### Error State
- Error icon
- User-friendly error message (no technical details)
- Retry button
- Contact support link for persistent errors
- Example: "Something went wrong loading patients. [Retry] or [Contact Support]"

### Offline State (PWA)
- Offline indicator in header
- Disabled actions that require connectivity
- Message: "You're offline. Some features are unavailable."

---

## Error Pages

### `/404` — Not Found

**Content:**
- "Page not found" message
- Illustration
- Search suggestion
- Link to dashboard

---

### `/403` — Forbidden

**Content:**
- "Access denied" message
- Reason displayed:
  - "You don't have permission to view this page"
  - "MFA is required to access this page" → Link to `/settings/security/mfa`
  - "Please sign the required consent documents" → Link to `/consent`
- Link to dashboard or appropriate action

---

### `/500` — Server Error

**Content:**
- "Something went wrong" message
- Request ID for support reference
- Retry button
- Contact support link with pre-filled request ID

---

### `/offline` — No Internet (PWA)

**Content:**
- "You are offline" message
- Explanation that app requires internet for PHI security
- Retry connection button
- Note: No cached PHI is displayed per HIPAA policy

---

## API Error Handling

Standard error-to-redirect mapping:

| Error Code | HTTP Status | Handling |
|------------|-------------|----------|
| `UNAUTHORIZED` | 401 | Redirect to `/login?reason=session_expired` |
| `FORBIDDEN` | 403 | Display `/403` page |
| `CONSENT_REQUIRED` | 403 | Redirect to `/consent` |
| `MFA_REQUIRED` | 403 | Redirect to `/settings/security/mfa` with blocking modal |
| `NOT_FOUND` | 404 | Display `/404` page |
| `VALIDATION_ERROR` | 422 | Display inline form errors |
| `RATE_LIMITED` | 429 | Toast: "Too many requests. Please wait." |
| `SERVER_ERROR` | 500 | Display `/500` page |

---

## Accessibility

> [!IMPORTANT]
> All routes MUST meet WCAG 2.1 Level AA compliance. Healthcare applications serve users with diverse abilities, including vision, hearing, motor, and cognitive differences.

### General Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Keyboard Navigation** | All interactive elements accessible via Tab/Shift+Tab |
| **Focus Indicators** | Visible focus rings on all focusable elements |
| **Skip Links** | "Skip to main content" link at top of each page |
| **Color Contrast** | Minimum 4.5:1 for normal text, 3:1 for large text |
| **Text Scaling** | Support 200% browser zoom without horizontal scroll |
| **Screen Reader** | Semantic HTML, ARIA labels, live regions for updates |

### Focus Management

**Route Navigation:**
- Focus moves to main content heading (`<h1>`) on route change
- Announce page title to screen readers via `document.title`

**Modal Dialogs:**
- Trap focus within modal when open
- Return focus to trigger element on close
- `Escape` key closes modal

**Forms:**
- Focus first error field on validation failure
- Error messages linked to inputs via `aria-describedby`
- Clear error state announcements for screen readers

### Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `?` | Open keyboard shortcut help | Global |
| `/` | Focus search bar | Global |
| `Escape` | Close modal/panel | Modal open |
| `g` then `d` | Go to Dashboard | Global |
| `g` then `p` | Go to Patients | Staff/Provider |
| `g` then `m` | Go to Messages | Global |

> [!NOTE]
> Keyboard shortcuts are disabled when focus is in text input fields.

### ARIA Guidelines by Component

| Component | ARIA Requirements |
|-----------|-------------------|
| **Sidebar Navigation** | `nav` role, `aria-current="page"` for active item |
| **Data Tables** | `role="table"`, sortable columns with `aria-sort` |
| **Alert Banners** | `role="alert"`, `aria-live="assertive"` for errors |
| **Loading States** | `aria-busy="true"` on container, live region for completion |
| **Notifications** | `role="status"`, `aria-live="polite"` for new items |
| **Modals** | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` |
| **Date Pickers** | Full keyboard support, announcements for selected dates |
| **Autocomplete** | `role="combobox"`, `aria-expanded`, `aria-activedescendant` |

### Healthcare-Specific Considerations

1. **Medical Jargon:** Provide plain-language alternatives where possible
2. **Time-Sensitive Alerts:** Use `aria-live="assertive"` for appointment reminders
3. **Complex Data:** Offer summary views for patients with cognitive differences
4. **Session Timeout:** Warning modal must be keyboard accessible and screen reader announced
5. **Impersonation Banner:** Must be announced to screen readers when session starts

---

## Related Documentation

- [00 - Overview.md](./00%20-%20Overview.md) — Project overview and data model
- [01 - Review prompt.md](./01%20-%20Review%20prompt.md) — Technical requirements
- [03 - Implementation.md](./03%20-%20Implementation.md) — Implementation plan (Phase 3: Frontend)
- [05 - API Reference.md](./05%20-%20API%20Reference.md) — Backend API endpoints

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.2.0 | 2024-12-30 | **Security & Completeness Enhancements:** Added Account Lockout Policy (HIPAA §164.312(d) compliance). Added Password Change Session Invalidation documentation. Added Super Admin routes (`/super-admin/*`). Added Proxy Assignment routes (`/patients/:id/proxies/*`). Added Provider Availability Management route. Added SSE event subscription documentation with reconnection behavior. |
| 2.1.0 | 2024-12-30 | Review findings addressed: Added `/dashboard` route with role-based content variations. Fixed `/proxy/patients` API path to primary endpoint. Added patient sub-routes (`/patients/:id/appointments`, `/patients/:id/messages`). Added `/appointments/:id/reschedule` route. Added `/admin/staff/new` and `/admin/providers/new` routes. Added `/notifications` route and notification panel documentation. Added comprehensive impersonation session management documentation. Fixed `/messages/new` API call to correct endpoint. Added Accessibility section with WCAG 2.1 AA requirements. |
| 2.0.0 | 2024-12-30 | Major update: Added Security & Session Management section, Appointments, Messaging, Call Center routes, Compliance routes, MFA setup, Onboarding flow, Help routes. Fixed API path inconsistencies. Added UI states documentation. Expanded permission matrix with Staff subcategories. |
| 1.0.0 | 2024-12-30 | Initial Frontend Views & Routes Reference |
