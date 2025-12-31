# Frontend Components & Views Analysis

This document maps the implementation requirements from `06 - Frontend Views & Routes.md` to the existing inventory of the available `shadcn-admin` template. It defines which components can be reused, which must be adapted, and which need to be created from scratch.

## Legend

- **[Existing]**: Component/View closely matches the requirement in `shadcn-admin` (`src/features/*` or `src/components/*`).
- **[Adapt]**: Component/View exists but requires significant modification (e.g., changing columns, data source, or logic).
- **[New]**: Component/View does not exist and must be created.
- **[UI Lib]**: Standard Shadcn UI component (`src/components/ui/*`) available for construction.

---

## 1. Global & Shared Components

| Component | Status | Source / Notes |
|-----------|--------|----------------|
| **App Shell / Layout** | [Adapt] | `src/routes/_authenticated/route.tsx` (Sidebar + Header layout) |
| **Sidebar Navigation** | [Adapt] | `src/features/layout/app-sidebar.tsx` (Update matching items from `06 - Routes`) |
| **Header** | [Adapt] | `src/features/layout/header.tsx` |
| **User Menu** | [Existing] | `src/components/profile-dropdown.tsx` |
| **Theme Switcher** | [Existing] | `src/components/theme-switch.tsx` |
| **Notification Bell** | [New] | Needs to be added to Header; Slide-out panel logic. |
| **Impersonation Banner** | [New] | Global persistent banner for "Break Glass" mode. |
| **Session Warning Modal** | [New] | Global inactivity timeout modal. |
| **Consent Banner** | [New] | Blockers for pending documents. |
| **Offline Indicator** | [New] | Network status detector. |
| **Loading Strategy** | [New] | Explicit requirement: All dynamic views MUST use `Skeleton` loaders mimicking content structure. |

---

## 2. Public Routes

### Landing Page (`/`)
- **View:** `LandingPage` **[New]**
- **Components:**
  - `HeroSection` [New]
  - `FeatureGrid` [New]
  - `Testimonials` [New]
  - `CTAButton` [UI Lib] (`Button`)

### Authentication
- **Login** (`/login`)
  - **View:** `SignInView` **[Existing]** (`src/features/auth/sign-in`)
  - **Components:** `UserAuthForm` [Adapt] (Add Google OAuth, specialized error handling).
- **Signup** (`/signup`)
  - **View:** `SignUpView` **[Existing]** (`src/features/auth/sign-up`)
  - **Components:** `SignUpForm` [Adapt] (Add Terms acceptance).
- **Forgot Password** (`/forgot-password`)
  - **View:** `ForgotPasswordView` **[Existing]** (`src/features/auth/forgot-password`)
- **Reset Password** (`/reset-password/:token`)
  - **View:** `ResetPasswordView` **[New]** (Can copy structure of ForgotPassword).
- **Verify Email** (`/verify-email/:token`)
  - **View:** `VerifyEmailView` **[Adapt]** (Use `src/features/auth/otp` as base).
- **Invite Evaluation** (`/invite/:token`)
  - **View:** `AcceptInviteView` **[New]**
  - **Components:** `InviteDetailsCard` [New].

### Legal Pages
- **View:** `LegalLayout` **[New]**
- **Routes:** `/legal/privacy`, `/legal/terms`
- **Component:** `MarkdownViewer` [New] (or simple static text).

---

## 3. Authenticated Routes

### Onboarding
- **Consent** (`/consent`)
  - **View:** `ConsentView` **[New]**
  - **Components:** `DocumentViewer` [New], `SignaturePad` or `CheckboxConsent` [New].
- **Onboarding Wizard** (`/onboarding`)
  - **View:** `OnboardingWizard` **[New]**
  - **Components:** `StepWizard` [New], `MfaSetupStep` [Adapt] (from `settings`), `ProfileSetupStep` [Adapt] (from `profile`).

### Dashboard (`/dashboard`)
- **View:** `DashboardView` **[Adapt]** (`src/features/dashboard/index.tsx`)
- **Requirements:** Role-based switching logic.
- **Components:**
  - `StatsCards` [Existing] (Adapt metrics).
  - `RecentActivity` [Existing] (Adapt data).
  - `UpcomingAppointments` [New Widget].
  - `TaskQueue` [New Widget] (Clinical only).
  - `QuickActions` [New Widget].

### Patients (`/patients`)
- **List View** (`/patients`)
  - **View:** `PatientsList` **[Adapt]** (Use `src/features/users/index.tsx` as template).
  - **Components:**
    - `PatientsTable` [Adapt] (`data-table` with Name, DOB, MRN columns).
    - `PatientFilters` [Adapt].
- **Create Patient** (`/patients/new`)
  - **View:** `CreatePatientView` **[New]** (Form).
- **Patient Detail** (`/patients/:id`)
  - **View:** `PatientDetailLayout` **[New]** (Header + Tabs).
  - **Components:**
    - `PatientHeader` [New] (Demographics banner).
    - `OverviewTab` [New].
    - `DocumentsTab` [New] (File upload/list).
    - `CareTeamTab` [New] (List of providers).
    - `HistoryTab` [New].

### Appointments (`/appointments`)
- **List View** (`/appointments`)
  - **View:** `AppointmentsView` **[New]**
  - **Components:**
    - `CalendarView` [New] (FullCalendar or similar).
    - `AppointmentList` [New] (Table view).
- **Booking** (`/appointments/new`)
  - **View:** `BookAppointmentView` **[New]**
  - **Components:** `ProviderSelect`, `TimeSlotPicker` [New].
- **Detail** (`/appointments/:id`)
  - **View:** `AppointmentDetailView` **[New]`.

### Messaging (`/messages`)
- **View:** `MessagingLayout` **[Adapt]** (`src/features/chats/index.tsx`)
- **Components:**
  - `ConversationList` [Adapt] (Add patient context/tags).
  - `MessageThread` [Adapt] (Support attachments, rich text).
  - `ComposeMessage` [New] (Modal or separate page).

### Call Center (`/call-center`)
- **View:** `CallCenterAgentView` **[New]**
- **Components:**
  - `ActiveCallPanel` [New].
  - `IncomingQueue` [New].
  - `QuickPatientSearch` [New].

### Providers (`/providers`)
- **View:** `ProviderDirectory` **[Adapt]** (Use `src/features/users/index.tsx` as template).
- **Components:** `ProviderCard` [New] (Grid view preference?).

### Admin Routes (`/admin/*`)
- **Organization Admin:**
  - `OrgDashboard` **[Adapt]** (`features/dashboard`).
  - `MemberManagement` (`/admin/members`) **[Adapt]** (`features/users`).
  - `StaffManagement` (`/admin/staff`) **[Adapt]** (`features/users` with specialized columns).
  - `ProviderManagement` (`/admin/providers`) **[Adapt]** (`features/users` with license columns).
  - `Billing` (`/admin/billing`) **[New]**.
  - `AuditLogs` (`/admin/audit-logs`) **[Adapt]** (Table view, heavily filtered).

### Super Admin Routes (`/super-admin/*`)
- **View:** `PlatformDashboard` **[Adapt]** (`features/dashboard`).
- **Org Management:** `OrgList` **[Adapt]** (`features/users`-like table).
- **User Management:** `UserList` **[Adapt]** (`features/users`).
- **System Health:** `SystemMetrics` **[New]** (Charts/Graphs).

### Settings (`/settings`)
- **Layout:** `SettingsLayout` **[Existing]** (`src/features/settings/index.tsx`).
- **Profile:** `ProfileForm` **[Existing]** (`src/features/settings/profile/profile-form.tsx`).
- **Account:** `AccountForm` **[Existing]** (`src/features/settings/account/account-form.tsx`).
- **Security:**
  - `SecuritySettings` **[New]**.
  - `MfaManager` [New].
  - `PasswordChange` [New] (Adapt `change-password-form` if exists, or create).
- **Communication:** `CommunicationPreferences` **[New]**.
- **Appearance:** `AppearanceForm` **[Existing]**.

### Help (`/help`)
- **View:** `HelpCenter` **[New]**.
- **Components:** `FaqAccordion` [Existing: `ui/accordion.tsx`], `ContactSupportForm` [New].

---

## 4. UI Library Mapping (Shadcn UI)

The following base components from `src/components/ui` will be heavily utilized:

- **Tables:** `table`, `data-table` (complex filtering/sorting).
- **Forms:** `form`, `input`, `select`, `checkbox`, `radio-group`.
- **Feedback:** `toast` (notifications), `alert`, `dialog` (modals).
- **Navigation:** `tabs` (Patient Detail), `dropdown-menu`, `navigation-menu`.
- **Layout:** `card` (Dashboard widgets), `resizable`, `scroll-area`.
- **Loading:** `skeleton` (for all loading states).

## 5. Summary of Work

1.  **High Reuse:** Auth views search as Login/Signup, Basic List views (Users), and Settings shell are ready to go.
2.  **Moderate Adapt:** Dashboard needs specific widgets. Chat needs healthcare context. User lists need specific columns for Staff/Providers.
3.  **High Effort / New:** Patient Detail (complex tabbed view), Appointments (Calendar), Onboarding Wizard, and specialized Admin functionality (Billing, System Health).

This analysis serves as the blueprint for the frontend implementation tasks.
