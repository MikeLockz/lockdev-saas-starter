# Story 10.4: Patient Frontend
**User Story:** As a Staff Member, I want a patient list and detail view, so that I can quickly find and manage patients.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.1 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/patients`, `/patients/:id`)

## Technical Specification
**Goal:** Implement patient list, detail, and form components.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/patients/`
    - `index.tsx` - Patient list page
    - `$patientId.tsx` - Patient detail page
    - `new.tsx` - Create patient form

2.  **Components:** `frontend/src/components/patients/`
    - `PatientTable.tsx`
      - Columns: Name, DOB, MRN, Status, Actions
      - Pagination controls
      - Search input (debounced)
      - Filter by status
    - `PatientForm.tsx`
      - All patient fields
      - Embedded ContactMethodsSection
    - `PatientDetail.tsx`
      - Header with name, MRN
      - Tabs: Overview, Contacts, Appointments (stub), Messages (stub)
    - `ContactMethodsSection.tsx`
      - List of contacts with edit/delete
      - Add new contact inline
      - "Safe for Voicemail" toggle with warning icon

3.  **Hooks:** `frontend/src/hooks/api/`
    - `usePatients.ts` - List with search params
    - `usePatient.ts` - Single patient detail
    - `useCreatePatient.ts` - Mutation
    - `useUpdatePatient.ts` - Mutation
    - `useContactMethods.ts` - CRUD operations

4.  **UX Details:**
    - Warning badge if contact not safe for voicemail
    - Confirmation dialog on delete
    - Toast on successful save

## Acceptance Criteria
- [ ] `/patients` displays paginated patient list.
- [ ] Search filters patients in real-time.
- [ ] `/patients/new` creates patient via form.
- [ ] `/patients/:id` shows full patient detail.
- [ ] Contact methods editable inline.
- [ ] Voicemail safety warning displayed.
- [ ] Stub tabs for Appointments/Messages shown.

## Verification Plan
**Automated Tests:**
- `pnpm test -- PatientTable` (component test)
- `pnpm test -- PatientForm` (form validation)

**Manual Verification:**
- Navigate to /patients, see list with search.
- Create new patient, verify appears in list.
- View patient, edit contact methods.
