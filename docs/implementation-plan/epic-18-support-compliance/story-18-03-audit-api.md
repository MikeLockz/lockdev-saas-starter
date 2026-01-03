# Story 18.3: Audit Log API
**User Story:** As an Auditor, I want to search audit logs for HIPAA compliance reviews.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.3 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Admin Endpoints")
- **Existing:** `AuditLog` model exists, logs being written

## Technical Specification
**Goal:** Implement audit log search API for compliance.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/audit.py` (NEW)
    - `AuditLogRead` (all fields)
    - `AuditLogSearchParams` (actor_id, resource_type, resource_id, action, date_from, date_to)

2.  **API Router:** `backend/src/api/admin.py` (UPDATE)
    - `GET /api/v1/admin/audit-logs`
      - Search audit logs with filters
      - Paginated results
      - Requires AUDITOR or SUPER_ADMIN role
    - `GET /api/v1/admin/audit-logs/{log_id}`
      - Single log detail with full context
    - `GET /api/v1/admin/audit-logs/export`
      - Export filtered logs as CSV
      - For compliance reporting

3.  **Search Capabilities:**
    - By actor (user who performed action)
    - By resource type (PATIENT, APPOINTMENT, etc.)
    - By resource ID
    - By action (READ, CREATE, UPDATE, DELETE)
    - By date range

## Acceptance Criteria
- [ ] `GET /admin/audit-logs` returns filtered results.
- [ ] Date range filtering works.
- [ ] Resource type filtering works.
- [ ] Export generates CSV.
- [ ] Only authorized roles can access.
- [ ] Accessing audit logs is itself audited.

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_audit.py`

**Manual Verification:**
- Perform actions, search in audit logs.
- Export CSV, verify content.
