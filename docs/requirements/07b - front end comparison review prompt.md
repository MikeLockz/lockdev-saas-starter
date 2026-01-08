You are a Senior Frontend Architect and QA Specialist. Your task is to perform a rigorous gap analysis and architectural review of the Frontend Component Map (`docs/07 - front end components.md`) against the authoritative Frontend Routes Reference (`docs/06 - Frontend Views & Routes.md`).

## Objectives
1.  **Verify Completeness:** Ensure every single route, view, and sub-view defined in `docs/06` has a corresponding implementation strategy in `docs/07`.
2.  **Validate Interactive Elements:** specific "Actions" listed in `docs/06` (buttons, forms, filters, toggles) must be represented by specific components or UI elements in `docs/07`.
3.  **Check State Coverage:** `docs/06` defines specific UI states (Loading, Empty, Error) for each route. Verify `docs/07` accounts for these, either through global patterns or specific components.
4.  **Audit Role Logic:** Verify that role-specific variations described in `docs/06` (e.g., "Provider Dashboard" vs "Patient Dashboard") are explicitly handled in the component architecture.

## Documents
-   **Source of Truth (Requirements):** `docs/06 - Frontend Views & Routes.md`
-   **Implementation Plan (Target):** `docs/07 - front end components.md`
-   **Existing Codebase:** `shadcn-admin` (reference for "Modify" vs "New")

## Review Instructions

### Step 1: Route-by-Route Verification
Iterate through every section of `docs/06`. For each route:
-   **Check:** Is this route present in `docs/07`?
-   **Check:** Does the listed component composition in `docs/07` support *all* "Content" and "Actions" listed in `docs/06`?
    -   *Example:* If `docs/06` says "Search input (name, MRN)" for the Patient List, does `docs/07` explicitly list a search component/input?
    -   *Example:* If `docs/06` lists "Upload area (drag-and-drop)", does `docs/07` include a `FileUploadZone`?
-   **Mark:** Any route or feature found in `06` but missing from `07` as a **Critical Gap**.

### Step 2: Deep Dive - Logic & Permissions
-   **Permission Matrix Audit:** `docs/06` contains specific permission matrices (e.g., for Patient Details). Verify if `docs/07` mentions how these permissions will be handled in the UI (e.g., "Conditional rendering based on `can_view_clinical_notes`").
-   **Form Validation:** For routes with forms (Signup, Patient Intake), does `docs/07` specify the necessary validation schemas? (e.g., "Safe for voicemail" checkbox, Password complexity rules).
-   **Complex Flows:** For multi-step flows like **/onboarding**, verify that `docs/07` lists a component for *each* step defined in `docs/06`.

### Step 3: Global & Functional Requirements
-   **Security UI:** `docs/06` mandates a "Session Timeout Warning" and "Impersonation Banner". Are these correctly mapped in `docs/07`?
-   **Navigation:** Does the `AppSidebar` or nav structure in `docs/07` account for the role-based menu items described in `docs/06`?
-   **Feedback:** Do the component definitions include success/error states (toasts, alerts) required by the "States" sections of `docs/06`?
-   **Accessibility & Mobile:** Does `docs/07` mention mobile considerations (e.g., using `Sheet` instead of `Dialog` on mobile, or collapsing sidebars) as implied by the modern standards in `docs/06`?

### Step 4: Component Reusability & Source
-   **Reuse Analysis:** Check specific components in `docs/07` marked as "**New**". Are there existing `shadcn` components that could be used instead?
-   **Modification Clarity:** For components marked "**Modify**", is the modification instruction clear enough for a developer to execute without guessing? (e.g. "Add 'Organization Selector' to Header" vs just "Update Header").

## Output Format
Generate your response in Markdown. Use the following structure:

### 1. Executive Summary
*Brief assessment of the coverage. (e.g., "90% coverage detailed, with 3 missing routes and 2 vague component definitions.")*

### 2. Critical Gaps (Must Fix)
*List specific routes or features from `docs/06` that are effectively invalid or entirely missing in `docs/07`. Use a checklist format.*
- [ ] **Route:** `[Route Name]`
  - **Gap:** [Description of what is missing]
  - **Requirement:** [Quote from docs/06]

### 3. Logic & State Inconsistencies
*List instances where component logic (permissions, validation, states) is missing or vague.*
- **Component:** `[Component Name]`
- **Issue:** [e.g., "No mention of conditional rendering for Proxy vs Provider view"]
- **Impact:** [Why this matters]

### 4. Architectural Suggestions
*Any recommendations to improve reusability, performance, or clarity based on the comparison.*

### 5. Validated Items (Green Check)
*Brief list of complex sections that are **correctly** and **fully** mapped. This helps confirm what is ready to build.*
