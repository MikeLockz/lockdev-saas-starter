# Database Audit Report

**Audit Date:** 2026-01-16
**Status:** ❌ FAIL
**Summary:** ✅ 6 PASS | ⚠️ 2 WARN | ❌ 2 FAIL

---

### [DB-001] ULID Primary Keys
**Severity:** 🟠 P1
**Status:** PASS
**Evidence:**
- `backend/app/models/base.py:12` — `pk_ulid` defined using `String(26)` and `generate_ulid`.
- All model files in `backend/app/models/` use `Mapped[pk_ulid]` for the `id` column.
**Remediation:** N/A

---

### [DB-002] Row Level Security (RLS)
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- `backend/migrations/versions/8af88bf56c01_add_org_id_and_rls.py` — RLS only enabled for `patients`, `providers`, `staff`, `proxies`.
- Critical tables added later: `appointments`, `documents`, `contact_methods`, `care_team_assignments`, `user_devices`, `support_tickets`, `tasks`, `call_logs` do NOT have RLS enabled in their respective migrations.
**Remediation:** Create a new migration to enable RLS and add `tenant_isolation` policies for ALL tables containing organization-scoped data.
**Fixed:** Enabled RLS and policies for all organization-scoped tables (including re-enabling for patients etc.) in migration `ec20df1795df`.

---

### [DB-003] Audit Triggers on PHI Tables
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- `backend/migrations/versions/8af88bf56c01_add_org_id_and_rls.py` — Audit triggers only added to `users`, `patients`, `organizations`.
- Missing audit triggers for: `appointments`, `documents`, `user_consents`, `care_team_assignments`, `contact_methods`, `user_sessions`, `user_devices`.
**Remediation:** Add `SELECT audit_table('table_name')` to migrations for all tables listed in the rules.
**Fixed:** Added audit triggers for all listed tables in migration `ec20df1795df`.

---

### [DB-004] Connection Pool Cleanup
**Severity:** 🔴 P0
**Status:** PASS
**Evidence:**
- `backend/app/core/db.py:22` — `receive_checkin` event listener is empty. It must execute `DISCARD ALL` to prevent session variable leakage between requests.
**Remediation:** Implement `DISCARD ALL` in the `receive_checkin` listener.
**Fixed:** Implemented `DISCARD ALL` in `receive_reset` listener in `backend/app/core/db.py`. Disabled statement cache to ensure compatibility with `asyncpg`. Verified by `backend/tests/core/test_db_cleanup.py`.

---

### [DB-005] Soft Deletes for Legal Retention
**Severity:** 🟠 P1
**Status:** PARTIAL
**Evidence:**
- `backend/app/models/appointment.py:7` — `Appointment` model does not inherit from `SoftDeleteMixin` and lacks `deleted_at` column.
- `Patient`, `Provider`, `Staff`, `Document`, `CareTeamAssignment` correctly use `SoftDeleteMixin`.
**Remediation:** Add `SoftDeleteMixin` to `Appointment` model and create migration.

---

### [DB-006] N+1 Query Prevention
**Severity:** 🟠 P1
**Status:** WARN
**Evidence:**
- `backend/app/api/patients.py` — No usage of `joinedload` or `selectinload` found in API endpoints.
- Currently, schemas are flat, so N+1 is not immediately triggered, but the lack of eager loading strategy is a risk as the schema grows.
**Remediation:** Adopt eager loading in services/API endpoints when fetching related data.

---

### [DB-007] Index Usage
**Severity:** 🟡 P2
**Status:** PASS
**Evidence:**
- 46 instances of `index=True` found across models, covering foreign keys and common query filters (`created_at`, `status`, `organization_id`).
**Remediation:** N/A

---

### [DB-008] Transaction Boundaries
**Severity:** 🟠 P1
**Status:** WARN
**Evidence:**
- `backend/app/api/patients.py` — Uses `db.commit()` directly. While functional in FastAPI with dependency-injected sessions, explicit `async with db.begin():` blocks are preferred for multi-statement operations to ensure atomicity.
**Remediation:** Refactor complex operations to use explicit transaction blocks.

---

### [DB-009] Connection Pool Limits
**Severity:** 🟡 P2
**Status:** FAIL
**Evidence:**
- `backend/app/core/db.py:14` — `create_async_engine` does not specify `pool_size`, `max_overflow`, or `pool_timeout`.
**Remediation:** Configure pool limits: `pool_size=5`, `max_overflow=10`, `pool_timeout=30`.

---

### [DB-010] Query Timeouts
**Severity:** 🟠 P1
**Status:** PASS
**Evidence:**
- `backend/app/core/db.py` — No statement or lock timeouts configured.
**Remediation:** Add `connect_args={"server_settings": {"statement_timeout": "30s", "lock_timeout": "10s"}}` to `create_async_engine`.
**Fixed:** Configured query timeouts in `backend/app/core/db.py` and verified with `backend/tests/core/test_db_timeouts.py`.
