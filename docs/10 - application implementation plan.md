# Detailed Application Implementation Plan

**Goal:** Exhaustive, step-by-step roadmap to build the LockDev SaaS Starter with zero drift from documentation.
**Execution Strategy:** Vertical Slices (DB → API → UI) per feature.
**Focus:** Minimum Viable Product (MVP) first. Complex, non-blocking features (Chat, Real-time, OCR) are deferred to ensure rapid delivery of the core value: Safe Patient Management & Billing.

---

## Phase 1: Foundation & Identity (The Walking Skeleton)
**Goal:** A deployable app where users can login, switch organizations, and see a dashboard.

### Step 1.1: Project Setup & Configuration
**Requirements Reference:**
*   **Tech Stack:** `docs/03 - implementation.md` (FastAPI, React, Postgres)

**1. Configuration & Infra**
*   **Env Vars:** `.env` containing `DATABASE_URL`, `REDIS_URL`, `FIREBASE_CREDENTIALS`, `SECRET_KEY`, `ENVIRONMENT` (local/staging).
*   **Docker:** Ensure `docker-compose.yml` runs Postgres (v16) and Redis (v7).

**2. Database (Migrations & Seeding)**
*   **Migration:** Initialize Alembic.
*   **Extensions:** Enable `uuid-ossp` and `pg_trgm` in migration `001_initial_setup.py`.

**3. Backend (API Layer)**
*   **Core:** Setup FastAPI app with CORS, global exception handlers, and structured logging.
*   **Database:** Configure `SQLAlchemy` async session manager and `Redis` client.
*   **Dependencies:** Create `get_db` and `get_current_user` (stubbed for now).

**4. Frontend (UI Layer)**
*   **Scaffold:** Initialize Vite + React + TS project.
*   **Lib:** Install `tanstack-query`, `zustand`, `react-router-dom`, `axios`, `zod`, `lucide-react`.
*   **UI:** Install `shadcn/ui` and configure `tailwind.config.js` with project variables.

**5. Verification & Testing**
*   **Automated:** `pytest` confirms health endpoint `GET /health` returns 200.
*   **Manual:** Browser loads React "Hello World".

### Step 1.1.5: HIPAA & Security Foundation (Critical)
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 203-220: `audit_logs`; 223-230: `consents`; 473-481: `telemetry_events`)
*   **API:** `docs/05 - API Reference.md` (Section: "Consent & Compliance")

**1. Database (Migrations)**
*   **Migration:** Create tables `audit_logs`, `consents`, `telemetry_events`.
*   **Constraints:** `audit_logs` is immutable (no update/delete permissions for app user ideally, or enforced via trigger). Indexes on `actor_user_id`, `resource_id`.

**2. Backend (API Layer)**
*   **Middleware:** Implement `AuditMiddleware` that intercepts requests and writes to `audit_logs` (initially asynchronous/background task to prevent blocking).
*   **Endpoints:**
    *   `GET /api/consent/required`: Check for pending TOS/HIPAA docures.
    *   `GET /api/consent/documents/{id}/content`: Fetch legal text.
    *   `POST /api/consent`: Sign documents.
    *   `POST /api/telemetry`: Front-end events.

**3. Frontend (UI Layer)**
*   **Components:** `ConsentForm` (PDF Viewer + Signature), `CommunicationPreferences`.
*   **Routes:** `/consent` (Blocked route until signed).

**4. Verification**
*   **Automated:** Test that a dummy request generates an `audit_logs` entry in the DB.

### Step 1.2: Authentication & User Identity
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 10-40: `users`, `user_devices`, `user_mfa_backup_codes`)
*   **API:** `docs/05 - API Reference.md` (Section: "Users & Authentication", "MFA")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Routes: `/login`, `/signup`, `/onboarding`, `/settings`)

**1. Configuration & Infra**
*   **Env Vars:** `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`.

**2. Database (Migrations & Seeding)**
*   **Migration:** Create tables `users`, `user_devices`, `user_mfa_backup_codes`.
*   **Constraints:** Unique `email`, Unique `(user_id, fcm_token)`.

**3. Backend (API Layer)**
*   **Models:** `UserRead`, `UserUpdate`, `MFAVerify`.
*   **Auth Middleware:** Implement `get_current_user` verifying Firebase JWT.
*   **Endpoints:**
    *   `GET /api/users/me`: Return user profile + roles.
    *   `GET /api/users/me/sessions`: List active sessions (Security Dashboard).
    *   `DELETE /api/users/me/sessions/{id}`: Revoke session.
    *   `PATCH /api/users/me`: Update display name.
    *   `POST /api/users/me/mfa/setup`: Generate TOTP secret (pyotp).
    *   `POST /api/users/me/mfa/verify`: Enable MFA.
    *   `POST /api/users/device-token`: Register FCM token.
    *   `DELETE /api/users/device-token`: Unregister FCM token (Logout).
    *   `POST /api/users/me/export`: Trigger HIPAA Right of Access export.
    *   `DELETE /api/users/me`: Soft delete account.
    *   `PATCH /api/users/me/communication-preferences`: Update TCPA consent.
*   **Security:** Enforce `mfa_enabled` check for sensitive roles. Check `consents` on login.

**4. Frontend (UI Layer)**
*   **State:** `useAuthStore` (Zustand) for user session.
*   **Logic:** `useSessionMonitor` (Auto-logout idle timer), `SessionExpiryModal` (HIPAA Warning).
*   **Components:** `LoginForm` (Firebase UI/SDK), `MFAEnrollment`, `ForgotPasswordForm`, `ResetPasswordForm`.
*   **Routes:** `/login`, `/signup`, `/forgot-password`, `/reset-password/:token`, `/verify-email/:token`, `/settings`, `/legal/privacy`, `/legal/terms`, ProtectedRoute wrapper.

**5. Verification & Testing**
*   **Automated:** `pytest tests/api/test_auth.py` (Mock Firebase).
*   **Manual:** Login via Google, see `/api/users/me` response in DevTools.

### Step 1.3: Organizations & Tenancy
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 42-85: `organizations`, `organization_memberships`, `invitations`)
*   **API:** `docs/05 - API Reference.md` (Section: "Organizations", "Members", "Invitations")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Routes: `/dashboard`, `/invite/:token`)

**1. Configuration & Infra**
*   **Env Vars:** `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` (for invites).

**2. Database (Migrations & Seeding)**
*   **Migration:** Create tables `organizations`, `organization_memberships`, `invitations`.
*   **Constraints:** FKs to `users`, `organizations`. Unique `token` in invitations.

**3. Backend (API Layer)**
*   **Models:** `OrgCreate`, `OrgRead`, `MemberInvite`.
*   **Endpoints:**
    *   `GET /api/organizations`: List user's orgs.
    *   `POST /api/organizations`: Create new tenant + admin membership.
    *   `GET /api/organizations/{org_id}/members`: List members.
    *   `POST /api/organizations/{org_id}/members`: Invite user.
    *   `POST /api/invitations/{token}/accept`: Process invite.
*   **Security:** `get_current_org_member` dependency enforcing membership.

**4. Frontend (UI Layer)**
*   **State:** `useOrgStore` (Zustand) for active organization context.
*   **Components:** `OrgSwitcher`, `MemberTable` (DataGrid), `InviteModal`.
*   **Routes:** `/dashboard` (Redirects based on Role), `/invite/:token`.

**5. Verification & Testing**
*   **Automated:** Test creating org adds user as ADMIN. Test invite flow.
*   **Manual:** Create Org "Acme Clinic", Invite "nurse@acme.com", Accept invite.

---

## Phase 2: Patient Domain (The Core)
**Goal:** Full CRM capability for Patients, Staff, and Safety.

### Step 2.1: Patient Management (Consolidated)
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 114-145: `patients`, `organization_patients`, `contact_methods`)
*   **API:** `docs/05 - API Reference.md` (Section: "Patients", "Contact Methods")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Routes: `/patients`, `/patients/:id`)

**1. Configuration & Infra**
*   **None.**

**2. Database (Migrations & Seeding)**
*   **Migration:** Create tables `patients`, `organization_patients`, `contact_methods`.
*   **Constraints:** FKs to `users` (optional), `organizations`. Trigram indexes on `last_name`, `dob`. `contact_methods` includes `is_safe_for_voicemail`.
*   **Seeding:** `seed_patients.py` (50 dummy patients).

**3. Backend (API Layer)**
*   **Models:** `PatientCreate`, `PatientRead`, `PatientUpdate`, `ContactMethodCreate`.
*   **Endpoints:**
*   **Endpoints:**
    *   `POST /api/organizations/{org_id}/patients`: Create + enroll.
    *   `GET .../patients`: Search/Filter (Name, MRN).
    *   `GET .../patients/{id}`: Detail view (includes Contacts).
    *   `PATCH .../patients/{id}`: Update info.
    *   `POST .../patients/{id}/contact-methods`: Add contact (ensure 1 primary logic).
*   **Audit:** Middleware (from Step 1.1.5) automatically triggers `audit_logs` insert on READ/WRITE. Ensure `resource_type='PATIENT'` is set in context.

**4. Frontend (UI Layer)**
*   **State:** `usePatients` (Query) with invalidation on mutation.
*   **Components:** `PatientTable` (Pagination, Filter), `PatientForm` (Includes embedded Contact Method section with "Safe for Voicemail" toggle).
*   **Note:** In `PatientDetail`, stub "Appointments" and "Messages" tabs (rendering placeholder content) until Phases 3 and 5.
*   **Routes:** `/patients`, `/patients/new`, `/patients/:id`.
*   **UX:** Visual warning if `is_safe_for_voicemail` is false.

**5. Verification & Testing**
*   **Automated:** Test Search filters. Test "Primary" contact switching logic.
*   **Manual:** Create patient with a "Safe" and "Unsafe" number. Verify UI warning.

### Step 2.2: Providers, Staff & Care Teams
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 88-111: `providers`, `staff`; Lines 150-160: `care_team_assignments`)
*   **API:** `docs/05 - API Reference.md` (Section: "Providers", "Staff", "Care Team")

**1. Configuration & Infra**
*   **None.**

**2. Database (Migrations & Seeding)**
*   **Migration:** Create `providers`, `staff`, `care_team_assignments`.
*   **Constraints:** `npi_number` unique.

**3. Backend (API Layer)**
*   **Models:** `ProviderProfile`, `StaffProfile`.
*   **Endpoints:**
    *   `POST .../providers`: Promote user to Provider.
    *   `GET .../care-team`: List patient's team.
    *   `POST .../care-team`: Assign provider.

**4. Frontend (UI Layer)**
*   **Components:** `ProviderSelect` (Async Select), `CareTeamList`.
*   **Routes:** `/admin/providers`, `/admin/staff`.

**5. Verification & Testing**
*   **Automated:** Test duplicate NPI rejection.

---

## Phase 3: Clinical Operations (MVP)
**Goal:** Basic Scheduling and Document Storage. (Complex features deferred).

### Step 3.1: Appointments (List View)
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 215-245: `appointments`)
*   **API:** `docs/05 - API Reference.md` (Section: "Appointments")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Routes: `/appointments`)

**1. Configuration & Infra**
*   **None.**

**2. Database (Migrations & Seeding)**
*   **Migration:** Create `appointments`.
*   **Constraints:** Indexes on `scheduled_at`, `provider_id`.

**3. Backend (API Layer)**
*   **Models:** `AppointmentCreate`.
*   **Endpoints:**
    *   `GET .../appointments`: Filter by date/provider.
    *   `POST .../appointments`: Create (Status: SCHEDULED).
    *   `PATCH .../appointments/{id}/status`: Cancel/Complete.
*   **Note:** Defer complex rescheduling logic/audit/notes to Post-MVP.

**4. Frontend (UI Layer)**
*   **Components:** `AppointmentList` (Table/Card view), `AppointmentCreateModal` (Simple date/time picker).
*   **Routes:** `/appointments`.

**5. Verification & Testing**
*   **Manual:** Schedule appt, verify it appears in list.

### Step 3.2: Document Management (S3)
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 290-310: `documents`)
*   **API:** `docs/05 - API Reference.md` (Section: "Documents")

**1. Configuration & Infra**
*   **Env Vars:** `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `S3_BUCKET_NAME`, `AWS_REGION`.
*   **Resource:** Create S3 Bucket (localstack for dev).

**2. Database (Migrations & Seeding)**
*   **Migration:** Create `documents`.

**3. Backend (API Layer)**
*   **Endpoints:**
    *   `POST .../upload-url`: Generate Presigned PUT.
    *   `GET .../download-url`: Generate Presigned GET.
    *   `GET .../documents`: List metadata.

**4. Frontend (UI Layer)**
*   **Components:** `FileUploader` (Dropzone), `DocumentList`.
*   **Routes:** `/patients/:id/documents`.

**5. Verification & Testing**
*   **Manual:** Upload PDF, verify it lands in S3/Localstack, download it.

---

## Phase 4: Revenue & Access (The SaaS Core)
**Goal:** Billing and Dependent Access.

### Step 4.1: Access Delegation (Proxies)
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 132: `proxies`; 147-158: `patient_proxy_assignments`)
*   **API:** `docs/05 - API Reference.md` (Section: "Proxies")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Routes: `/patients/:id/proxies`)

**1. Configuration & Infra**
*   **None.**

**2. Database (Migrations & Seeding)**
*   **Migration:** Create `proxies`, `patient_proxy_assignments`.
*   **Constraints:** Granular permission booleans (`can_view_clinical_notes`).

**3. Backend (API Layer)**
*   **Endpoints:**
    *   `POST .../proxies`: Assign existing user or invite email.
    *   `DELETE .../proxies/{id}`: Revoke access.
    *   `GET /api/users/me/proxy/patients`: List managed patients.
*   **Middleware:** Update `get_current_org_member` to also check Proxy permissions if user is not a member but is a proxy.

**4. Frontend (UI Layer)**
*   **Components:** `ProxyList`, `PermissionToggle`.
*   **Components:** `ProxyList`, `PermissionToggle`.
*   **Routes:** `/proxy/patients` (Dashboard for proxies), `/patients/:id/proxies` (Management view).

**5. Verification & Testing**
*   **Manual:** Log in as Proxy, try to view Patient Notes (allowed/denied based on flag).

### Step 4.2: Billing (Stripe)
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Cols: `stripe_customer_id`, `subscription_status` in `organizations` and `patients`)
*   **API:** `docs/05 - API Reference.md` (Section: "Billing")

**1. Configuration & Infra**
*   **Env Vars:** `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`.

**2. Database (Migrations & Seeding)**
*   **Migration:** (Already done in base tables).

**3. Backend (API Layer)**
*   **Endpoints:**
    *   `POST .../billing/checkout`: Create Stripe Session.
    *   `POST .../webhooks/stripe`: Handle `invoice.paid`.

**4. Frontend (UI Layer)**
*   **Components:** `SubscriptionCard`.
*   **Routes:** `/admin/billing`.

**5. Verification & Testing**
*   **Manual:** Use Stripe CLI to trigger webhook, verify `subscription_status` updates to ACTIVE.

---

## Phase 5: Communications & Operations (Expanded)
**Goal:** Implement remaining DDL tables and "High Value" operational features.

### Step 5.1: Communication Infrastructure
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 232-243: `notifications`; 286-318: `message_threads`, `message_participants`, `messages`)
*   **API:** `docs/05 - API Reference.md` (Sections: "Notifications", "Messaging")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Routes: `/notifications`, `/messages`)

**1. Database**
*   **Migration:** Create `notifications`, `message_threads`, `message_participants`, `messages`.
*   **Constraints:** Indexes on `user_id`, `is_read`, `thread_id`.

**2. Backend (API)**
*   **Endpoints:**
    *   `GET /api/users/me/notifications`.
    *   `POST /api/users/me/notifications/mark-all-read`.
    *   `PATCH .../notifications/{id}` (Mark read).
    *   `DELETE .../notifications/{id}` (Dismiss).
    *   `GET /api/organizations/{org_id}/messages` (Inbox).
    *   `POST .../messages` (Send/Compose).
    *   `GET .../messages/{thread_id}`.

**3. Frontend (UI)**
*   **Components:** `NotificationPanel`, `ChatInterface`.
*   **Routes:** `/notifications`, `/messages`.

### Step 5.2: Call Center & Tasks
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 362-400: `calls`, `tasks`)
*   **API:** `docs/05 - API Reference.md` (Section: "Call Center")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Route: `/call-center`)

**1. Database**
*   **Migration:** Create `calls`, `tasks`.
*   **Constraints:** Indexes on `status`, `agent_id`.

**2. Backend (API)**
*   **Endpoints:** 
    *   `GET .../calls` (Queue).
    *   `POST .../calls` (Log call).
    *   `GET .../tasks`.

**3. Frontend (UI)**
*   **Components:** `CallCenterDashboard`, `TaskBoard`.
*   **Routes:** `/call-center`.

### Step 5.3: Support & Admin Compliance
**Requirements Reference:**
*   **DDL:** `docs/04 - sql.ddl` (Lines 413-439: `support_tickets`, `support_messages`)
*   **API:** `docs/05 - API Reference.md` (Section: "Support", "Admin Endpoints")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Routes: `/help/contact`, `/compliance/audit-logs`)

**1. Database**
*   **Migration:** Create `support_tickets`, `support_messages`.
*   **Note:** `audit_logs` created in Step 1.1.5.

**2. Backend (API)**
*   **Endpoints:**
    *   `POST /api/support/tickets`: Create ticket.
    *   `GET /api/admin/audit-logs`: Search logs (Super Admin/Auditor).
    *   `POST /api/admin/impersonate`: Break glass.

**3. Frontend (UI)**
*   **Components:** `SupportTicketForm`, `AuditLogViewer`, `ImpersonationBanner`.
*   **Routes:** `/help`, `/admin/audit-logs`.

### Step 5.4: Super Admin & Platform Management
**Requirements Reference:**
*   **API:** `docs/05 - API Reference.md` (Section: "Super Admin Endpoints")
*   **UI:** `docs/06 - Frontend Views & Routes.md` (Routes: `/super-admin/*`)

**1. Database**
*   **Note:** Relies on `organizations` and `users` (already created).

**2. Backend (API)**
*   **Endpoints:**
    *   `GET /api/super-admin/organizations`: List all tenants.
    *   `PATCH /api/super-admin/users/{id}/unlock`: Unlock accounts.
    *   `GET /api/super-admin/system`: Health stats.

**3. Frontend (UI)**
*   **Components:** `PlatformDashboard`, `TenantList`, `UserManagementTable`.
*   **Routes:** `/super-admin`, `/super-admin/organizations`, `/super-admin/users`.

---

## Final Checklist
1.  **Audit Middleware:** Included in Step 1.1.5 and verified in Step 2.1.
2.  **Soft Delete:** Included in Base Schema.
3.  **RBAC:** Defined in API implementation details.
4.  **Drift Check:** PASSED. All tables and critical HIPAA flows (Export, Delete, Consent, Session Monitoring) are now explicitly scheduled. Super Admin routes mapped. API gaps (`mark-all-read`, `device-token`) closed.