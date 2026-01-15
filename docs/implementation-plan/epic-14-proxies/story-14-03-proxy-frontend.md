# Story 14.3: Proxy Frontend
**User Story:** As a Patient, I want a UI to manage my proxies, and as a Proxy, I want to see my dependents.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.1 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/proxy/patients`, `/patients/:id/proxies`)

## Technical Specification
**Goal:** Implement proxy management and dashboard UI.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/`
    - `proxy/patients.tsx` - Proxy dashboard (patients I manage)
    - `patients/$patientId/proxies.tsx` - Manage patient's proxies

2.  **Components:** `frontend/src/components/proxies/`
    - `ProxyList.tsx`
      - Table of assigned proxies
      - Shows name, email, relationship, permissions
      - Edit/revoke buttons
    - `ProxyAssignModal.tsx`
      - Email input
      - Relationship dropdown
      - Permission toggles
    - `PermissionToggle.tsx`
      - Individual permission switch
      - Grouped by category (View, Actions)
    - `ProxyPatientCard.tsx`
      - Patient card for proxy dashboard
      - Shows patient name, relationship, quick actions

3.  **Hooks:** `frontend/src/hooks/api/`
    - `usePatientProxies.ts` - List proxies
    - `useMyProxyPatients.ts` - Patients I'm proxy for
    - `useAssignProxy.ts` - Mutation
    - `useUpdateProxyPermissions.ts` - Mutation

4.  **Integration:**
    - Add Proxies tab to PatientDetail
    - Add proxy dashboard to sidebar for proxy users

## Acceptance Criteria
- [ ] `/patients/:id/proxies` shows proxy list.
- [ ] Can add proxy via modal with permissions.
- [ ] Permission toggles update immediately.
- [ ] Can revoke proxy access.
- [ ] `/proxy/patients` shows managed patients.
- [ ] Proxy dashboard only visible to proxy users.

## Verification Plan
**Automated Tests:**
- `pnpm test -- ProxyList`
- `pnpm test -- PermissionToggle`

**Manual Verification:**
- Add proxy to patient, verify in list.
- Log in as proxy, verify dashboard shows patient.
