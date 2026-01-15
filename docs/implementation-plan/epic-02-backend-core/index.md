# Epic 2: Backend Core
**User Story:** As a Backend Developer, I want a secure, HIPAA-compliant backend with robust authentication and data models, so that I can safely store and access patient data.

**Goal:** Production-ready backend with strict HIPAA controls: UUIDs, Role Separation, MFA, and Consent tracking.

## Traceability Matrix
| Roadmap Step (docs/03) | Story File | Status |
| :--- | :--- | :--- |
| Step 2.1 | `story-02-01-config.md` | Pending |
| Step 2.2 | `story-02-02-database.md` | Pending |
| Step 2.3 | `story-02-03-migrations.md` | Pending |
| Step 2.4 | `story-02-04-models.md` | Pending |
| Step 2.5 | `story-02-05-auth.md` | Pending |
| Step 2.6 | `story-02-06-impersonation.md` | Pending |
| Step 2.7 | `story-02-07-consent.md` | Pending |
| Step 2.8 | `story-02-08-admin.md` | Pending |

## Execution Order
1.  [ ] `story-02-01-config.md`
2.  [ ] `story-02-02-database.md`
3.  [ ] `story-02-03-migrations.md`
4.  [ ] `story-02-04-models.md`
5.  [ ] `story-02-05-auth.md`
6.  [ ] `story-02-06-impersonation.md`
7.  [ ] `story-02-07-consent.md`
8.  [ ] `story-02-08-admin.md`

## Epic Verification
**Completion Criteria:**
- [ ] Database schema deployed with Alembic.
- [ ] Users can authenticate via Firebase/GCIP.
- [ ] Role-based access control works (Patient vs Staff).
- [ ] MFA is enforced for Staff.
- [ ] Audit logs capture critical actions.
- [ ] Impersonation works and is logged.
