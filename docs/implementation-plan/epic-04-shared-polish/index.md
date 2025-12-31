# Epic 4: Shared Polish & Infrastructure
**User Story:** As an SRE, I want observability, security, and automated infrastructure, so that the system is production-ready and auditable.

**Goal:** Logging, Audits, and Production Prep.

## Traceability Matrix
| Roadmap Step (docs/03) | Story File | Status |
| :--- | :--- | :--- |
| Step 4.1 | `story-04-01-logging.md` | Pending |
| Step 4.2 | `story-04-02-audit-rls.md` | Pending |
| Step 4.2b | `story-04-02b-read-audit.md` | Pending |
| Step 4.3 | `story-04-03-aws-opentofu.md` | Pending |
| Step 4.4 | `story-04-04-background-worker.md` | Pending |
| Step 4.5 | `story-04-05-aptible-deploy.md` | Pending |
| Step 4.6 | `story-04-06-dns-certs.md` | Pending |
| Step 4.7 | `story-04-07-policy-code.md` | Pending |

## Execution Order
1.  [ ] `story-04-01-logging.md`
2.  [ ] `story-04-02-audit-rls.md`
3.  [ ] `story-04-02b-read-audit.md`
4.  [ ] `story-04-03-aws-opentofu.md`
5.  [ ] `story-04-04-background-worker.md`
6.  [ ] `story-04-05-aptible-deploy.md`
7.  [ ] `story-04-06-dns-certs.md`
8.  [ ] `story-04-07-policy-code.md`

## Epic Verification
**Completion Criteria:**
- [ ] Logs are JSON formatted and masked.
- [ ] RLS policies enforce tenant isolation.
- [ ] Read access to PHI is logged.
- [ ] Infra code passes Checkov scan.
- [ ] Deployment pipeline works.
