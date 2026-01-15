# Story 11.4: Provider & Care Team Frontend
**User Story:** As an Admin, I want a UI to manage providers, and as a Patient, I want to see my care team.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.2 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/admin/providers`, `/admin/staff`)

## Technical Specification
**Goal:** Implement provider management UI and care team display.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/admin/`
    - `providers/index.tsx` - Provider list
    - `providers/new.tsx` - Add provider form
    - `staff/index.tsx` - Staff list
    - `staff/new.tsx` - Add staff form

2.  **Components:** `frontend/src/components/providers/`
    - `ProviderTable.tsx` - List with NPI, specialty, status
    - `ProviderForm.tsx` - NPI input with validation
    - `StaffTable.tsx` - Staff listing
    - `StaffForm.tsx` - Staff creation

3.  **Components:** `frontend/src/components/patients/`
    - `CareTeamList.tsx` - Display assigned providers
    - `CareTeamAssignModal.tsx` - Assign provider to patient
    - `ProviderSelect.tsx` - Async select for choosing provider

4.  **Hooks:** `frontend/src/hooks/api/`
    - `useProviders.ts` - List providers
    - `useStaff.ts` - List staff
    - `useCareTeam.ts` - Care team operations

5.  **Integration:**
    - Add CareTeamList to PatientDetail page
    - Add "Assign Provider" button

## Acceptance Criteria
- [x] `/admin/providers` lists all providers.
- [x] Provider form validates NPI format.
- [x] `/admin/staff` lists all staff members.
- [x] Patient detail shows care team list.
- [x] Can assign provider from patient detail.
- [x] ProviderSelect shows searchable dropdown.

## Verification Plan
**Automated Tests:**
- `pnpm test -- ProviderForm` (NPI validation)
- `pnpm test -- ProviderSelect` (async loading)

**Manual Verification:**
- Navigate to /admin/providers, add provider.
- Go to patient detail, assign care team member.
