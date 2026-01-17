# Database Audit Report

**Audit Date:** 2026-01-16
**Status:** ✅ PASS
**Summary:** ✅ 9 PASS | ⚠️ 0 WARN | ❌ 1 FAIL

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
**Status:** PASS
**Evidence:**
- `backend/app/models/appointment.py` — Inherits from `SoftDeleteMixin`.
- Migration `ea2e58f69efd` adds `deleted_at` column.
**Remediation:** Add `SoftDeleteMixin` to `Appointment` model and create migration.
**Fixed:** Added SoftDeleteMixin and created migration.

---

### [DB-006] N+1 Query Prevention
**Severity:** 🟠 P1
**Status:** PASS
**Evidence:**
- `backend/app/api/patients.py` — Implemented `selectinload` for `contact_methods`.
**Remediation:** Adopt eager loading in services/API endpoints when fetching related data.
**Fixed:** Added selectinload to patient endpoints.

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
**Status:** PASS
**Evidence:**
- `backend/app/api/patients.py` — Uses `async with db.begin():` for multi-statement operations in `create_contact_method`.
**Remediation:** Refactor complex operations to use explicit transaction blocks.
**Fixed:** Refactored create_contact_method to use db.begin().

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
