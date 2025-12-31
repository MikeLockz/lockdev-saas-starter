# Component Mapping Task

You are tasked with architecting the component structure for the Lockdev SaaS Front End. You must map the requirements defined in the documentation to the existing resources in the reference boilerplate, identifying gaps where custom components are needed.

## Inputs
1.  **Requirements**: `docs/06 - Frontend Views & Routes.md` (Defines views, content, and actions).
2.  **Reference Component Library**: `/Users/mbp/Development/shadcn-admin` (Contains existing Shadcn components and views).

## Instructions

### 1. Explore Reference Inventory
First, explore the `/Users/mbp/Development/shadcn-admin` repository. Standard Shadcn implementations usually place components in `src/components/ui` or `components/ui`. Look for:
-   **Atomic UI Components**: (e.g., Button, Input, Card, Dialog).
-   **Composed/Block Components**: (e.g., Sidebar, UserNav, complex Forms).
-   **Layouts**: (e.g., DashboardLayout, AuthLayout).

*Goal*: Understand exactly what is "off-the-shelf" so we don't reinvent the wheel.

### 2. Map Views to Components
Go through **every route/view** defined in `docs/06 - Frontend Views & Routes.md`. For each view, generate a detailed specification:

1.  **Layout & Structure**: Identify the wrapping layout and main structural containers (Grid, Flex, Sidebar).
2.  **Component Composition**:
    -   **Reuse**: List standard components from the reference repo that fit directly (e.g., "Use `Card` for the container, `Table` for the list").
    -   **New/Custom**: Identify where a custom component is required (e.g., "We need a `PatientActionMenu`").
3.  **Detailed Breakdown for New Components**:
    For every *new* or *custom* component (one not in `shadcn-admin`), be explicit:
    -   **Name**: Semantic name (e.g., `AppointmentRescheduleModal`).
    -   **Atoms**: What base components build this? (e.g., "Composed of `Dialog`, `Calendar`, `Select`, `Button`").
    -   **Form Elements**: If it's a form, list every field.
        -   Example: "Fields: Patient Name (Input), Type (Select), Date (DatePicker), Notes (Textarea)".
    -   **Interactions**: What does it trigger? (e.g., "On submit, calls API").

### 3. Output Requirements
Write the final detailed inventory to `docs/07 - front end components.md`.

**Format Specification:**
Organize by Route >> Section >> Component.

Example:
```markdown
## /patients/:id (Patient Detail)
**Layout:** Dashboard Layout
**Page Components:**
- `PatientHeader` (New)
  - Composition: `Avatar`, `Heading`, `Badge` (Status)
  - Actions: "Edit Profile" (`Button`)
- `PatientTabs` (Existing: `Tabs`)
  - Triggers: Overview, Documents, Care Team...
- `OverviewTab Content`
  - `DemographicsCard` (New)
    - Composition: `Card`, `DescriptionList`
```

Ensure NO view from `docs/06` is skipped. COMPREHENSIVENESS is key.
