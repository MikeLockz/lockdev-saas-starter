# Story 21.5: Organization Switcher Enhancement
**User Story:** As a user with multiple organization associations, I want to easily switch between organizations, so that I can manage different contexts.

## Status
- [ ] **Pending** (Partial implementation exists)

## Context
- **Related:** `epic-08-organizations/story-08-03-org-frontend.md`
- **Component:** `OrgSwitcher.tsx`

## Technical Specification
**Goal:** Ensure all user types can switch organization context appropriately.

**Current Implementation:**
- `OrgSwitcher` shows organizations where user is `OrganizationMember`
- Selecting org updates `useCurrentOrg()` context

**Gaps for Multi-Association Users:**

### Patient with Multiple Orgs
- Patient can be enrolled in multiple orgs (`OrganizationPatient`)
- Need: Surface patient's orgs in OrgSwitcher (different from member orgs)
- API: `GET /users/me/patient-organizations` (NEW or enhance existing)

### Proxy with Multiple Patients Across Orgs
- Proxy patients may span multiple organizations
- Need: Show unique orgs from proxy's patient assignments
- API: Already available via `/users/me/proxy-patients`

### Provider/Staff in Multiple Orgs
- Already supported via `OrganizationMember`
- Existing OrgSwitcher works correctly

**Changes Required:**

### Backend
1.  **Endpoint Enhancement:** `GET /users/me/organizations`
    - Include orgs from:
      - `OrganizationMember` (staff/provider/admin)
      - `OrganizationPatient` (if patient)
      - `PatientProxyAssignment → Patient → OrganizationPatient` (if proxy)
    - Response: Deduplicated list with role context

### Frontend
1.  **OrgSwitcher Enhancement:**
    - Group orgs by access type (Member, Patient, Proxy)
    - Show role badge for each org
    - Handle edge case: user has overlapping access types

2.  **Role-Aware Navigation:**
    - When switching orgs, update sidebar based on role in that org
    - Patient accessing their org → show patient dashboard
    - Staff accessing same org → show staff features

## Acceptance Criteria
- [ ] User sees all orgs they can access (any role/relationship).
- [ ] Orgs grouped by access type for clarity.
- [ ] Switching orgs updates entire app context.
- [ ] Navigation/sidebar reflects role in selected org.
- [ ] Works for: Admin, Staff, Provider, Patient, Proxy.

## Verification Plan
**Manual Verification:**
- Create user with multiple org associations.
- Verify OrgSwitcher shows all orgs.
- Switch between orgs, verify UI updates correctly.
