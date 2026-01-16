# Epic 8: Organizations & Tenancy
**User Story:** As an Organization Admin, I want to manage my organization and invite team members, so that we can collaborate on patient care.

**Goal:** Multi-tenant organization management with member invitations and role assignment.

## Traceability Matrix
| Plan Step (docs/10) | Story File | Status |
| :--- | :--- | :--- |
| Step 1.3 (Org API) | `story-08-01-org-api.md` | Complete |
| Step 1.3 (Invitations) | `story-08-02-invitations.md` | Complete |
| Step 1.3 (Frontend) | `story-08-03-org-frontend.md` | Complete |
| Step 1.3 (Invite UI) | `story-08-04-invite-ui.md` | Complete |
| DB Review Fix | `story-08-05-counter-maintenance.md` | Complete |

## Execution Order
1.  [x] `story-08-01-org-api.md`
2.  [x] `story-08-02-invitations.md`
3.  [x] `story-08-03-org-frontend.md`
4.  [x] `story-08-04-invite-ui.md`
5.  [x] `story-08-05-counter-maintenance.md`

## Epic Verification
**Completion Criteria:**
- [x] User can list their organizations.
- [x] User can create a new organization (becomes ADMIN).
- [x] Admin can view organization members.
- [x] Admin can invite users by email.
- [x] Invited user receives email and can accept.
- [x] OrgSwitcher component allows switching context.
- [x] Member table shows all org members with roles.
- [ ] Organization `member_count` and `patient_count` stay accurate.
