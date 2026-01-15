# Epic 21: User-Organization Association
**User Story:** As a system administrator, I want all user types (staff, providers, patients, proxies) to be properly associated with organizations through consistent, secure flows, so that multi-tenant data isolation is maintained.

**Goal:** Comprehensive user-organization linking system covering all association methods: invitations, patient self-service, proxy assignment, and admin-initiated links.

## Traceability Matrix
| Plan Step (docs/10) | Story File | Status |
| :--- | :--- | :--- |
| Staff/Provider Invite | `story-21-01-staff-provider-invite.md` | Pending |
| Patient Self-Claim | `story-21-02-patient-self-claim.md` | Pending |
| Admin Patient Link | `story-21-03-admin-patient-link.md` | Pending |
| Proxy Patient Access | `story-21-04-proxy-patient-access.md` | Pending |
| Org Switcher Enhancement | `story-21-05-org-switcher-enhancement.md` | Pending |

## Execution Order
1.  [ ] `story-21-01-staff-provider-invite.md` - Existing invite flow (already implemented, verify)
2.  [ ] `story-21-02-patient-self-claim.md` - NEW: Patient claims their record
3.  [ ] `story-21-03-admin-patient-link.md` - NEW: Admin links user to patient
4.  [ ] `story-21-04-proxy-patient-access.md` - Proxy gains access via patient assignment
5.  [ ] `story-21-05-org-switcher-enhancement.md` - Multi-org patient/proxy support

## Epic Verification
**Completion Criteria:**
- [ ] Staff/Provider can join org via email invitation (existing).
- [ ] Patient can sign up and claim their existing patient record.
- [ ] Admin can manually link a user account to a patient record.
- [ ] Proxy can access patient data through proxy assignment.
- [ ] User can switch between organizations if they belong to multiple.
- [ ] All association methods are audited.

## User-Organization Association Matrix

| User Type | Association Method | Data Relationship |
|-----------|-------------------|-------------------|
| **Staff** | Invite → Accept | `OrganizationMember.user_id` |
| **Provider** | Invite → Accept | `OrganizationMember.user_id` + `Provider.organization_id` |
| **Admin** | Invite → Accept | `OrganizationMember.user_id` (role=ADMIN) |
| **Patient** | Claim OR Admin Link | `Patient.user_id` + `OrganizationPatient` |
| **Proxy** | Assigned by Admin | `PatientProxyAssignment.proxy_id → Patient → OrganizationPatient` |
