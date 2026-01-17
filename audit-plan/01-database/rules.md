# Database Audit Rules

## Scope
- `backend/src/models/` — SQLAlchemy models
- `backend/src/database.py` — Engine and session config
- `backend/migrations/` — Alembic migrations

---

## Rules

### DB-001: ULID Primary Keys
**Severity:** 🟠 P1  
**Requirement:** ALL tables must use ULID (not UUID or serial int) for primary keys.  
**Rationale:** Prevents ID enumeration attacks, allows lexicographical sorting.  
**Check:**
```bash
grep -r "Column.*Integer.*primary" backend/src/models/
grep -r "Column.*UUID" backend/src/models/
```
**Expected:** No matches. All PKs should use `ULID` type from `python-ulid`.

---

### DB-002: Row Level Security (RLS)
**Severity:** 🔴 P0  
**Requirement:** RLS policies must be enabled on all PHI tables using `app.current_tenant_id`.  
**Tables:** `patient`, `appointment`, `document`, `contact_method`, `care_team_assignment`  
**Check:**
```sql
SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';
```
**Migration Check:**
```bash
grep -r "CREATE POLICY" backend/migrations/
grep -r "ENABLE ROW LEVEL SECURITY" backend/migrations/
```

---

### DB-003: Audit Triggers on PHI Tables
**Severity:** 🔴 P0  
**Requirement:** All PHI tables must have audit triggers logging INSERT/UPDATE/DELETE to `audit_logs`.  
**Check:**
```bash
grep -r "CREATE TRIGGER.*audit" backend/migrations/
```
**Verify Table List:** `user`, `patient`, `provider`, `staff`, `appointment`, `document`, `user_consent`, `care_team_assignment`, `contact_method`, `user_session`, `device`

---

### DB-004: Connection Pool Cleanup
**Severity:** 🔴 P0  
**Requirement:** Session variables must be cleared on connection return to pool via `DISCARD ALL`.  
**Rationale:** Prevents cross-request tenant leakage in async pools.  
**Check:**
```bash
grep -r "DISCARD ALL" backend/src/database.py
grep -r "checkin" backend/src/database.py
```
**Expected:** Event listener on `engine.sync_engine` `checkin` event executing `DISCARD ALL`.

---

### DB-005: Soft Deletes for Legal Retention
**Severity:** 🟠 P1  
**Requirement:** Clinical data tables must use soft deletes (`deleted_at` timestamp) instead of hard deletes.  
**Tables:** `patient`, `appointment`, `document`, `care_team_assignment`  
**Check:**
```bash
grep -r "deleted_at" backend/src/models/
```
**Additional:** Verify no `DELETE FROM` statements in application code (only in migrations for cleanup).

---

## General Best Practices

### DB-006: N+1 Query Prevention
**Severity:** 🟠 P1  
**Requirement:** Queries must avoid N+1 patterns using eager loading (`joinedload`, `selectinload`).  
**Check:**
```bash
grep -r "joinedload\|selectinload\|subqueryload" backend/src/
```
**Anti-Pattern Check:**
```bash
# Look for loops that might cause N+1
grep -rA5 "for.*in.*query\|for.*in.*await" backend/src/api/ backend/src/services/
```

---

### DB-007: Index Usage
**Severity:** 🟡 P2  
**Requirement:** Foreign keys and frequently queried columns must have indexes.  
**Check:**
```bash
grep -r "Index\|index=True" backend/src/models/
```
**Common Columns:** `created_at`, `organization_id`, `user_id`, `status`

---

### DB-008: Transaction Boundaries
**Severity:** 🟠 P1  
**Requirement:** Database operations must use explicit transaction boundaries. No auto-commit for multi-step operations.  
**Check:**
```bash
grep -r "async with.*session\|session.begin\|commit()" backend/src/api/ backend/src/services/
```

---

### DB-009: Connection Pool Limits
**Severity:** 🟡 P2  
**Requirement:** Connection pools must have appropriate size limits to prevent resource exhaustion.  
**Check:**
```bash
grep -r "pool_size\|max_overflow\|pool_timeout" backend/src/database.py backend/src/config.py
```
**Expected:** `pool_size=5`, `max_overflow=10`, `pool_timeout=30` (adjust for load)

---

### DB-010: Query Timeouts
**Severity:** 🟠 P1  
**Requirement:** Database operations must have timeouts to prevent hanging queries.  
**Check:**
```bash
grep -r "statement_timeout\|lock_timeout" backend/src/database.py
grep -r "timeout" backend/src/config.py
```
