# Role
You are a Lead Product Manager and Data Architect specializing in Healthcare SaaS (HIPAA constraints) and Product-Led Growth (PLG).

# Task
Create a comprehensive **Frontend Telemetry & Analytics Implementation Plan**.
Output file: `docs/11 - frontend analytics.md`

# Context & Constraints
*   **Privacy-First:** We operate under a strict "Log, Don't Track" policy. We do NOT use third-party analytics pixels (Google Analytics, Mixpanel, etc.) to avoid BAA complications and PII leakage.
*   **Mechanism:** Behavioral events are sent to our own backend via `POST /api/telemetry`. The backend logs them to CloudWatch via `structlog`.
*   **Separation of Concerns:**
    *   **Sentry:** Used for *Application Health* (Crashes, API Latency, React Render Errors).
    *   **Telemetry:** Used for *User Behavior* (Funnel completion, Feature adoption, Business logic errors).

**Reference Documents:**
1.  `docs/06 - Frontend Views & Routes.md` (The User Flows)
2.  `docs/07 - front end components.md` (The UI Components to instrument)
3.  `docs/08 - front end state management.md` (The `useAnalytics` hook)
4.  `docs/05 - API Reference.md` (The API Schema)

# Objectives for the Output Document

## 1. Define Key Performance Indicators (KPIs)
Before defining events, define *what* we are measuring.
*   **Activation Rate:** % of signups who schedule their first appointment.
*   **Network Virality:** % of Providers who invite Staff; % of Patients who invite Proxies.
*   **Utilization:** Appointments scheduled per Active Provider per Week.
*   **Completion Rate:** % of started onboarding flows that finish.

## 2. Comprehensive Event Registry
Create a structured table for all events. Mapping **must** be specific to components in `docs/07`.

| Event Name | Trigger Condition | Properties (Safe) | Properties (UNSAFE - DO NOT SEND) | Component (from docs/07) |
| :--- | :--- | :--- | :--- | :--- |
| `appointment_scheduled` | User confirms booking | `provider_specialty`, `visit_type` | `patient_name`, `reason_for_visit` | `AppointmentWizard` |

**Required Domains to Cover:**
1.  **Auth/Onboarding:** Signup, Email Verify, Consent (Accepted/Declined), MFA Setup.
2.  **Patient Management:** Search (count only), Create Patient (success/fail), View Details.
3.  **Appointments:** Funnel steps (Select Provider -> Date -> Confirm), Reschedule, Cancel.
4.  **Messaging:** Thread Started, Message Sent (attachment count only).
5.  **Proxy/Network:** Invite Sent, Invite Accepted.

## 3. Implementation Strategy (Code Level)
Provide concrete code examples using the `useAnalytics` hook defined in `docs/08`.
*   **Example 1: Wizard Tracking.** How to track step progression in `OnboardingWizard`.
*   **Example 2: Action Tracking.** How to track a "Search" action without logging the search term (PHI).
*   **Example 3: Error Tracking.** How to log a "Business Logic Error" (e.g., "Quota Exceeded") distinct from a crash.

## 4. Privacy & Compliance Rules (The "Red List")
Explicitly define what constitutes PHI in this system and providing "Sanitization Rules".
*   *Example:* Never log `patient_id` if it maps back to a person easily? Actually, `patient_id` (ULID) IS generally safe in internal logs if access controlled, but `patient_name` is NOT. Clarify this distinction.
*   **Strict Rule:** No free-text input fields (search queries, message bodies, notes) can ever be sent to telemetry.

# Deliverable Structure
1.  **Executive Summary:** The "Log, Don't Track" philosophy.
2.  **Growth KPIs:** What metrics drive these events.
3.  **Event Taxonomy:** The master table (Grouped by Feature).
4.  **Implementation Guide:** Code snippets for React components.
5.  **Privacy Checklist:** Rules for developers to follow when adding new events.

**Analyze the reference documents to ensure the event registry matches the actual features and components of Lockdev SaaS.**