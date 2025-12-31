# Story 4.2: Audit Logging & Row Level Security (RLS)
**User Story:** As a Compliance Officer, I want strict data isolation and an immutable audit trail, so that we meet HIPAA requirements.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 4.2 from `docs/03`

## Technical Specification
**Goal:** Implement RLS policies and Audit triggers.

**Changes Required:**
1.  **Migration:**
    - Create `audit_logs` table.
    - Create Trigger to record `INSERT/UPDATE/DELETE` with `actor_id`.
    - Enable RLS on `patient_profile` and other sensitive tables.
    - Create Policy: `tenant_isolation` using `app.current_tenant_id`.
2.  **Code:** Ensure `set_session_context` (Epic 2) is correctly populating the variables.

## Acceptance Criteria
- [ ] User A cannot query User B's data (RLS).
- [ ] All writes generate an Audit Log entry.

## Verification Plan
**Automated Tests:**
- Create two tenants. Insert data for Tenant A. Try to read as Tenant B -> Expect 0 rows.
- Insert data -> Query `audit_logs` -> Expect 1 row.
