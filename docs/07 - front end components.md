# Frontend Component Architecture & Mapping

This document maps the user requirements from `docs/06 - Frontend Views & Routes.md` to the implementation strategy, utilizing the `shadcn-admin` reference implementation where possible and defining new components where gaps exist.

## 1. Global & Shared Components

these components appear across multiple views or provide fundamental layout structure.

### Loading Strategy & Skeletons
**Requirement:** All components that fetch data or load asynchronously **MUST** display a visual loading state (Skeleton) that approximates the final content structure. This minimizes Cumulative Layout Shift (CLS) and provides better UX than generic spinners.

-   **Implementation:** Use the `Skeleton` primitive from `src/components/ui/skeleton`.
-   **Pattern:**
    -   Create dedicated skeleton components for complex views (e.g., `DashboardSkeleton`, `PatientProfileSkeleton`).
    -   Use generic compositions for standard elements (e.g., `TableSkeleton`, `CardListSkeleton`).
    -   Wrap dynamic regions in `Suspense` or conditional `isLoading` checks rendering the skeleton.

### State Feedback
**Requirement:** Consistent handling of API states (Error, Empty, Forbidden) across the app.
-   `ErrorState`: Generic error boundary or inline error with "Retry" button.
-   `EmptyState`: Illustrated component with "Create [Item]" CTA.
-   `RoleGuard`: Wrapper component to handle permission checks (`<RoleGuard permission="can_view_billing">`).
-   `WizardShell`: Layout wrapper for multi-step forms (Step indicator + Navigation buttons).

### Layouts
| Component | Status | Source/Definition | Notes |
|-----------|--------|-------------------|-------|
| `RootLayout` | **Existing** | `src/main.tsx` + Router | Logic for auth checking & routing |
| `AuthenticatedLayout` | **Existing** | `src/components/layout/authenticated-layout.tsx` | Main app shell with Sidebar and Header. Needs customization for Lockdev specific links. |
| `PublicLayout` | **New** | — | Simple wrapper for marketing/public pages (Header + Footer). |
| `AuthLayout` | **Existing** | `src/features/auth/auth-layout.tsx` | Centered card layout for Login/Signup. |

### Global UI Elements
| Component | Status | Source/Definition | Description |
|-----------|--------|-------------------|-------------|
| `AppSidebar` | **Modify** | `src/components/layout/app-sidebar.tsx` | Modify navigation items to match Lockdev roles (Patients, Appointments, etc.). |
| `Header` | **Modify** | `src/components/layout/header.tsx` | Add Organization Selector, Global Search, Notification Bell. |
| `NotificationPanel` | **New** | — | **Atoms:** `Sheet` (Slide-out), `ScrollArea`, `Tabs` (All/Unread).<br>**Content:** List of `NotificationItem` components.<br>**Interactions:** Click to mark read/navigate. |
| `SessionExpiryModal` | **New** | — | **Atoms:** `Dialog`, `Progress` (for countdown), `Button`.<br>**Logic:** Triggers on `idle` events. |
| `ImpersonationBanner` | **New** | — | **Atoms:** `div` (sticky top), `Alert` styling.<br>**Content:** "Impersonating [Patient]..." + Exit Button. |
| `ConsentBanner` | **New** | — | **Atoms:** `Alert` (sticky bottom/top).<br>**Logic:** Shows if `user.pending_consents.length > 0`. |
| `WizardShell` | **New** | — | **Composition:** `Stepper`, content area, `Button` row (Back/Next).<br>**Usage:** Onboarding, Proxy Invite, Appointments. |

---

## 2. Public Routes

### `/` (Landing Page)
- **Layout:** `PublicLayout`
- **Component:** `LandingPage` (New)
  - **Composition:** 
    - `HeroSection` (Heading, Subheading, CTA Buttons)
    - `FeatureGrid` (Cards with Icons)
    - `TestimonialCarousel` (`Carousel` ui component)
    - `Footer`

### `/login`, `/signup`, `/forgot-password`, `/reset-password`
- **Layout:** `AuthLayout`
- **Components:**
  - `LoginForm` (Modify `src/features/auth/sign-in/sign-in.tsx`)
  - `SignUpForm` (Modify `src/features/auth/sign-up/sign-up.tsx`)
  - `ForgotPasswordForm` (Modify `src/features/auth/forgot-password/forgot-password.tsx`)
  - `ResetPasswordForm` (New)
    - **Form Elements:** Password (Input), Confirm Password (Input).
    - **Validation:** Zod schema for complexity.

---

## 3. Authenticated Routes

### Onboarding & Consent

#### `/consent`
- **Layout:** `AuthLayout` (or minimal `AuthenticatedLayout`)
- **Component:** `ConsentManager` (New)
  - **Composition:** `Card`, `ScrollArea` (for legal text), `Checkbox` (Agreement).
  - **Interactions:** "Sign & Continue" requires scroll-to-bottom + checkbox.

#### `/onboarding`
- **Layout:** `AuthenticatedLayout` (Simplified nav)
- **Component:** `OnboardingWizard` (New)
  - **Composition:** `Stepper` (custom or library), `Card`.
  - **Steps:**
    1. `ProfileForm` (Name, Photo upload)
    2. `MfaSetup` (QR Code `img`, OTP `Input`, `Button` verify)
    3. `OrgSelection` (List of orgs or Join Invite code)

### Dashboard

#### `/dashboard`
- **Layout:** `AuthenticatedLayout`
- **Component:** `DashboardView` (New - Role Based Switcher)
  - **Sub-Components:**
    - `PatientDashboard`:
        - `UpcomingAppointmentsCard`: List of next 3 appts.
        - `CareTeamWidget`: Grid of small `UserAvatar` cards.
    - `ProviderDashboard`:
        - `StatsCards` (Review `src/features/dashboard/components/overview.tsx`)
        - `TodaySchedule`: Timeline view of appointments.
        - `TaskQueue`: List of pending items.
    - `StaffDashboard` (Clinical/Admin):
        - `TaskQueue`: Assigned tasks/approvals.
        - `PatientSearchWidget`: Quick look-up.
    - `AdminDashboard` (Org):
        - `OrgHealthMetrics`: Member count, Active Patients.
        - `SubscriptionStatusCard`: Billing overview.
    - `CallCenterDashboard`: Redirects to `/call-center`.

### Patients

#### `/patients` (List)
- **Layout:** `AuthenticatedLayout`
- **Component:** `PatientList` (Reuse/Modify `src/features/users/index.tsx`)
  - **Existing:** `DataTable` (Pagination, Sorting, Filtering).
  - **Modifications:** 
    - Columns: Name/Photo, MRN, DOB, Status, Actions.
    - Filters: Status (Active/Discharged), Provider.

#### `/patients/new`
- **Layout:** `AuthenticatedLayout`
- **Component:** `CreatePatientForm` (New)
  - **Composition:** `Form`, `Input`, `Select`, `DatePicker`, `Sheet` or `Page`.
  - **Fields:** Demographics, Contact Info, Primary Provider (`Combobox`).

#### `/patients/:id` (Detail Wrapper)
- **Layout:** `AuthenticatedLayout`
- **Component:** `PatientDetailView` (New)
  - **Composition:**
    - `PatientHeader` (New): Avatar, Name, MRN, Badges, Quick Actions (Edit, Message).
    - `PatientTabs` (Existing `Tabs`: Overview, Appointments, Messages, Documents, Care Team).

**Tab Contents:**
1. **Overview**: `PatientDemographics` (`Card`, `DescriptionList`), `NotesWidget`.
2. **Documents**: `DocumentManager` (New)
   - **Composition:** `DataTable` (Name, Date, Type, Status), `FileUploadZone` (Drag & drop).
   - **Features:** Virus Scan status icons (Pending/Clean/Infected).
   - **Actions:** Download, Preview (Dialog), Delete.
3. **Care Team**: `CareTeamList` (New)
   - **Composition:** Grid of `ProviderCard` components.
   - **Actions:** "Manage Team" (Modal).
4. **Appointments**: Reuse `AppointmentList` (Filtered by patient).
5. **Messages**: Reuse `ChatInterface` (Filtered by patient).
6. **Billing**: `PaymentMethodsList`, `SubscriptionStatus`.

#### `/patients/:id/proxies`
- **Component:** `ProxyManager` (New)
  - **Composition:** List of proxies.
  - **Actions:** Invite Proxy (Button).

#### `/patients/:id/proxies/invite`
- **Layout:** `AuthenticatedLayout`
- **Component:** `ProxyInviteWizard` (New)
  - **Wrapper:** `WizardShell`.
  - **Steps:**
    1. **Proxy Info:** Name, Email, Phone.
    2. **Relationship:** Type (Parent/Guardian/POA), Doc Upload (`FileUploadZone`).
    3. **Permissions:** Checkbox group (View Clinical, View Billing, Schedule, Message).
    4. **Confirm:** Summary + "Send Invitation".

---

### Appointments

#### `/appointments` (List/Calendar)
- **Layout:** `AuthenticatedLayout`
- **Component:** `AppointmentManager` (New)
  - **Views:** Toggle between `CalendarView` and `ListView` (`DataTable`).
  - **CalendarView:** Wrapper around `react-big-calendar` or `FullCalendar` (if added) or custom grid using `date-fns`.
  - **ListView:** Columns: Date, Time, Patient, Provider, Type, Status.

#### `/appointments/new`
- **Component:** `AppointmentWizard` (New)
  - **Composition:** `Stepper`, `Card`.
  - **Steps:**
    1. Select Patient (`Command`/`Combobox` search).
    2. Select Provider & Service (`Select`).
    3. Select Slot (`Calendar` day picker + Grid of time buttons).
    4. Confirm (`Textarea` for reason).

#### `/appointments/:id`
- **Component:** `AppointmentDetail` (New)
  - **Composition:** `Card` (Details), `Badge` (Status), `Button` (Reschedule/Cancel).
  - **Actions:** "Join Telehealth" (Primary Button).

#### `/appointments/:id/reschedule`
- **Component:** `AppointmentRescheduleView` (New)
  - **Composition:** 
    - `CurrentAppointmentSummary` (`Card`).
    - `ProviderAvailabilityCalendar` (Calendar view to pick new date).
    - `TimeSlotGrid` (Button selection).
  - **Actions:** Confirm Reschedule.

---

### Messaging

#### `/messages`
- **Layout:** `AuthenticatedLayout`
- **Component:** `ChatLayout` (Reuse `src/features/chats/index.tsx`)
  - **Structure:** 
    - `ChatSidebar` (Thread list, Search, Filters).
    - `ChatWindow` (Message list, Input area).
  - **Modifications:** 
    - Support for "System" messages in thread.
    - Attachments support (`FileIcon`, `Image`).
    - Infinite scroll for history.

#### `/messages/new`
- **Component:** `ComposeMessageDialog` (New/Overlay)
  - **Form Elements:** Recipient (`Combobox` multi-select), Subject (`Input`), Body (`Textarea`).

---

### Call Center

#### `/call-center`
- **Layout:** `AuthenticatedLayout`
- **Component:** `CallCenterDashboard` (New)
  - **Composition:** 3-Column Layout.
  - **Col 1 (Queue):** `IncomingCallList` (`Card` list with "Accept" button).
  - **Col 2 (Active):** `ActiveCallPanel` (Timer, Patient Info, Notes Form).
  - **Col 3 (History):** `RecentCallsList`.

---

### Staff & Providers

#### `/providers` & `/admin/staff`
- **Component:** `StaffList` (Reuse `src/features/users` pattern)
  - **Columns:** Name, Role, Status, Last Active.
  - **Actions:** Edit, Deactivate.

#### `/providers/:id`
- **Component:** `ProviderProfile` (New)
  - **Composition:** Header (Photo, Credentials), Tabs (Overview, Schedule, Patients).

---

### Admin

#### `/admin`
- **Component:** `AdminDashboard` (New)
  - **Composition:** High-level metrics charts (`Recharts`), Quick Link Grid.
  - **Role:** Org Admin only.

#### `/admin/impersonate`
- **Component:** `ImpersonationStartView` (New)
  - **Composition:** 
    - `PatientSearch` (`Command` list).
    - `ReasonForm` (`Input` required).
    - `RecentImpersonations` (`DataTable` history).
  - **Logic:** Triggers `useImpersonationStore` state update + banner.

#### `/admin/billing`
- **Component:** `OrganizationBilling` (New)
  - **Composition:** `PlanDetailsCard`, `PaymentMethodCard`, `InvoiceTable`.

#### `/compliance`
- **Component:** `ComplianceDashboard` (New)
  - **Composition:** `ComplianceScore` (Chart), `PendingReviewsList`.

#### `/compliance/audit-logs`
- **Component:** `AuditLogViewer` (New)
  - **Composition:** `DataTable` (optimized for large datasets).
  - **Filters:** Complex filter bar (Actor, Resource, Date Range).

---

### Settings

#### `/settings`
- **Layout:** `AuthenticatedLayout`
- **Component:** `SettingsLayout` (Reuse `src/features/settings/index.tsx`)
  - **Structure:** Sidebar navigation for settings sections (Profile, Security, etc.).

#### `/settings/security/mfa`
- **Component:** `MfaManager` (New)
  - **Composition:** Status Switch, "Setup" Button (triggers QR modal), "Backup Codes" (Dialog).

#### `/settings/communication`
- **Component:** `CommunicationPreferences` (New)
  - **Composition:** `Switch` group (Marketing, Transactional), `TimePicker` (Quiet Hours).

#### `/settings/security`
- **Component:** `SecuritySettings` (New)
  - **Composition:** `MfaStatus`, `PasswordChangeForm`, `ActiveSessionsList` (with "Revoke" action).

---

### Super Admin
*Platform-wide administration.*

#### `/super-admin`
- **Component:** `SuperAdminDashboard`
  - **Composition:** Platform metrics (Active Orgs, Total Users), System Health Widget.

#### `/super-admin/organizations`
- **Component:** `OrganizationManager`
  - **Composition:** `DataTable` (Orgs), `CreateOrgDialog`.

#### `/super-admin/users`
- **Component:** `PlatformUserManager`
  - **Composition:** `DataTable` (Users, filters by Org), `UnlockUserDialog`.

#### `/super-admin/system`
- **Component:** `SystemHealthDashboard`
  - **Composition:** `MetricsGrid` (API Latency, Error Rates), `ServiceStatusList`.

---

### Notification & Help

#### `/notifications`
- **Component:** `NotificationCenter` (New)
  - **Composition:** 
    - `NotificationFilterBar` (Tabs: All/Unread, Select: Type).
    - `NotificationList` (Paginated).
  - **Actions:** "Mark all read", "Delete".

#### `/help`
- **Component:** `HelpCenter` (New)
  - **Composition:** `SearchInput`, `FaqAccordion`, `VideoTutorialGrid`.

#### `/help/contact`
- **Component:** `SupportTicketForm` (New)
  - **Composition:** `Select` (Category), `Textarea`, `FileUpload` (Screenshot).

---

## 4. Implementation Priorities

1.  **Shared Layouts & Shell**: Ensure `AppSidebar` and `Header` support all roles.
2.  **Core Components**: `DataTable` (robust version), `SearchInput`, `StatusBadge`.
3.  **Patient & Appointment Flows**: These are the heart of the system.
4.  **Admin & Compliance**: Can reuse generic data tables initially.

## 5. Technology & Libraries
- **Tables**: `tanstack/react-table` (Existing in `shadcn-admin`).
- **Forms**: `react-hook-form` + `zod` (Existing).
- **Charts**: `recharts` (Need to verify if installed, standard for shadcn).
- **Icons**: `lucide-react` (Existing).
- **Calendar**: Need to evaluate `react-day-picker` (likely included with shadcn Calendar) vs full scheduler library for `/appointments`.
- **Loading**: `Skeleton` primitive (Existing in `shadcn/ui`) for all async states.
