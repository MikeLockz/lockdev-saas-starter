# Row-Level Security (RLS) Implementation Guide

## Overview

This document describes the Row-Level Security (RLS) implementation for the Lockdev SaaS Starter platform. RLS is a **critical HIPAA compliance requirement** that enforces tenant isolation at the database level, providing defense-in-depth against cross-tenant data leakage.

## Why RLS is Critical for HIPAA Compliance

### HIPAA Requirement: §164.308(a)(4)(ii)(B) - Access Control

HIPAA requires healthcare applications to implement:
- **Isolation of patient records** across different healthcare organizations
- **Technical safeguards** to prevent unauthorized access
- **Database-level enforcement** of access controls

### The Risk Without RLS

Application-level filtering alone is **NOT sufficient** for HIPAA compliance because:

1. **SQL Injection Attacks**: An attacker could bypass WHERE clauses
2. **Developer Errors**: A forgotten filter could expose all tenant data
3. **ORM Bugs**: Framework issues could leak cross-tenant data
4. **Direct Database Access**: Support tools might bypass application logic

### RLS as Defense-in-Depth

With RLS enabled:
- ✅ **Database enforces** tenant isolation automatically
- ✅ **Impossible to accidentally leak** cross-tenant data
- ✅ **Works even if** application code is buggy
- ✅ **Protects against** SQL injection at the data access layer
- ✅ **Meets HIPAA requirements** for technical safeguards

## Architecture

### Session Context Variables

RLS policies use PostgreSQL session variables to determine data access:

```sql
app.current_tenant_id  -- The organization_id for the current request
app.current_user_id    -- The user_id making the request
```

These variables **MUST** be set by the application layer at the start of each database transaction:

```python
# Python/SQLAlchemy example
async with session.begin():
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
        {"tenant_id": str(current_tenant_id)}
    )
    await session.execute(
        text("SELECT set_config('app.current_user_id', :user_id, true)"),
        {"user_id": str(current_user_id)}
    )
    # Now execute queries - RLS is active
    result = await session.execute(select(Patient))
```

### Super Admin Bypass

The `is_super_admin()` helper function allows platform administrators to bypass tenant isolation for support and administrative purposes.

```sql
CREATE OR REPLACE FUNCTION is_super_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM users
        WHERE id = current_setting('app.current_user_id', true)::UUID
          AND is_super_admin = true
          AND deleted_at IS NULL
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
```

**Security Note**: Super admin access should be:
- Logged in audit trails
- Protected with MFA
- Limited to specific named individuals
- Reviewed regularly

## Table-by-Table RLS Coverage

### Direct Tenant Scoping (organization_id column)

These tables have `organization_id` and policies filter directly:

| Table | Policy | Description |
|-------|--------|-------------|
| `organizations` | Self-access only | Each org sees only itself |
| `organization_memberships` | Filter by org_id | Users see only their org's memberships |
| `organization_patients` | Filter by org_id | Patient-org relationships scoped |
| `care_team_assignments` | Filter by org_id | Care teams scoped to organization |
| `audit_logs` | Filter by org_id | Audit logs scoped (with special INSERT policy) |

### Indirect Tenant Scoping (via relationships)

These tables are scoped through joins:

| Table | Scoped Via | Policy Logic |
|-------|-----------|--------------|
| `patients` | `organization_patients` | Patient visible if in current org |
| `providers` | `organization_memberships` | Provider visible if member of current org |
| `staff` | `organization_memberships` | Staff visible if member of current org |
| `proxies` | `patient_proxy_assignments` + `organization_patients` | Proxy visible if manages patient in current org |
| `contact_methods` | `patients` → `organization_patients` | Contact visible if patient is in current org |
| `patient_proxy_assignments` | `patients` → `organization_patients` | Assignment visible if patient in current org |
| `consents` | `patients` → `organization_patients` | Consent visible if patient in current org |

### Special Cases

#### Audit Logs - Immutability

Audit logs have **four separate policies**:

1. **INSERT**: Allowed for all authenticated users (needed for triggers)
2. **SELECT**: Scoped by organization_id
3. **UPDATE**: Blocked (always returns false)
4. **DELETE**: Blocked (always returns false)

This ensures audit logs are truly immutable while still being accessible for compliance reporting.

#### Users Table - No RLS (By Design)

The `users` table does **NOT** have RLS enabled because:
- Users are global entities that can belong to multiple organizations
- User access is controlled via `organization_memberships` RLS
- Application layer must filter user queries appropriately

If strict user isolation is required, the commented policy in `05 - rls_policies.sql` can be uncommented.

## Testing

Comprehensive RLS tests are provided in `06 - rls_tests.sql`. The test suite verifies:

### Test Coverage

1. **Cross-Tenant Isolation** (TEST 1 & 2)
   - Clinic A users cannot see Clinic B data
   - Clinic B users cannot see Clinic A data
   - All tenant-scoped tables are tested

2. **Super Admin Bypass** (TEST 3)
   - Super admins can see data across all tenants
   - Works for all tables

3. **Audit Log Immutability** (TEST 4)
   - UPDATE queries fail
   - DELETE queries fail
   - INSERT queries succeed

4. **Proxy Access Control** (TEST 5)
   - Proxies can see patients they manage
   - Proxies have self-access to their own records
   - Cross-tenant proxy access is blocked

5. **RLS Coverage Verification** (TEST 6)
   - All expected tables have RLS enabled
   - Verification query provided

6. **Policy Coverage Verification** (TEST 7)
   - All tables have appropriate policies
   - Policy counts are correct

### Running Tests

```bash
# 1. Set up test database
psql -d test_db -f docs/04\ -\ sql.ddl

# 2. Apply RLS policies
psql -d test_db -f docs/05\ -\ rls_policies.sql

# 3. Run tests
psql -d test_db -f docs/06\ -\ rls_tests.sql

# 4. Verify all assertions pass
# Expected: All COUNT queries return expected values
# Expected: UPDATE/DELETE on audit_logs raise errors
```

## Implementation Checklist

Before deploying to production, ensure:

- [ ] RLS policies applied to all tenant-scoped tables
- [ ] Application code sets `app.current_tenant_id` on every transaction
- [ ] Application code sets `app.current_user_id` on every transaction
- [ ] Super admin access is logged in audit trails
- [ ] All RLS tests pass successfully
- [ ] Integration tests verify cross-tenant isolation
- [ ] Performance testing confirms RLS doesn't cause issues
- [ ] Documentation is updated for developers

## Application Integration

### FastAPI Example

```python
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException

async def set_rls_context(
    session: AsyncSession,
    tenant_id: UUID,
    user_id: UUID
) -> None:
    """Set RLS context variables for the current transaction."""
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)}
    )
    await session.execute(
        text("SELECT set_config('app.current_user_id', :user_id, true)"),
        {"user_id": str(user_id)}
    )

async def get_db_with_rls(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Organization = Depends(get_current_tenant)
) -> AsyncSession:
    """Database session with RLS context already set."""
    async with session.begin():
        await set_rls_context(session, current_tenant.id, current_user.id)
        yield session
```

### Usage in Endpoints

```python
@router.get("/patients")
async def list_patients(
    db: AsyncSession = Depends(get_db_with_rls)
):
    # RLS automatically filters to current org - no manual filter needed!
    result = await db.execute(select(Patient))
    patients = result.scalars().all()
    return patients
```

## Performance Considerations

### Index Requirements

RLS policies use joins and subqueries. Ensure these indexes exist:

```sql
-- For organization_patients join
CREATE INDEX IF NOT EXISTS idx_org_patients_patient_id
ON organization_patients(patient_id);

CREATE INDEX IF NOT EXISTS idx_org_patients_org_id
ON organization_patients(organization_id);

-- For organization_memberships join
CREATE INDEX IF NOT EXISTS idx_org_memberships_user_id
ON organization_memberships(user_id);

CREATE INDEX IF NOT EXISTS idx_org_memberships_org_id
ON organization_memberships(organization_id);

-- For patient_proxy_assignments join
CREATE INDEX IF NOT EXISTS idx_patient_proxy_assignments_patient_id
ON patient_proxy_assignments(patient_id);

CREATE INDEX IF NOT EXISTS idx_patient_proxy_assignments_proxy_id
ON patient_proxy_assignments(proxy_id);
```

### Query Performance

RLS policies are applied **automatically** to all queries. PostgreSQL's query planner:
- ✅ Can use indexes effectively with RLS
- ✅ Optimizes policy checks
- ✅ Caches policy evaluation results

Monitor query performance with `EXPLAIN ANALYZE`:

```sql
EXPLAIN ANALYZE
SELECT * FROM patients WHERE last_name = 'Smith';
```

Look for:
- Index usage on foreign keys
- Reasonable plan costs
- No sequential scans on large tables

## Troubleshooting

### Common Issues

#### 1. "No rows returned" when data should exist

**Cause**: RLS context variables not set

**Solution**:
```sql
-- Check context
SELECT current_setting('app.current_tenant_id', true);
SELECT current_setting('app.current_user_id', true);

-- Should return UUIDs, not empty strings
```

#### 2. Super admin cannot see data

**Cause**: User's `is_super_admin` flag is false or `deleted_at` is set

**Solution**:
```sql
-- Verify super admin status
SELECT id, email, is_super_admin, deleted_at
FROM users
WHERE id = current_setting('app.current_user_id', true)::UUID;
```

#### 3. RLS policies blocking legitimate access

**Cause**: Policy logic is too restrictive

**Solution**: Review policy with `pg_policies`:
```sql
SELECT * FROM pg_policies WHERE tablename = 'your_table';
```

#### 4. Performance degradation

**Cause**: Missing indexes on foreign keys used in policy joins

**Solution**: Add indexes as shown in "Performance Considerations" section

## Security Best Practices

1. **Always Set Context Variables**
   - Never execute queries without setting `app.current_tenant_id`
   - Use middleware/decorators to enforce this

2. **Log Super Admin Access**
   - Record all queries executed with super admin privileges
   - Review logs regularly for suspicious activity

3. **Test RLS Regularly**
   - Include RLS tests in CI/CD pipeline
   - Run full test suite after schema changes

4. **Monitor for Bypass Attempts**
   - Alert on failed RLS policy checks
   - Log attempts to set invalid tenant_id

5. **Document Exceptions**
   - If a table doesn't have RLS, document why
   - Review exceptions during security audits

## Compliance Documentation

### HIPAA Technical Safeguards

This RLS implementation satisfies:

- ✅ **§164.308(a)(4)(ii)(B)** - Access Control
  - Isolation of patient records enforced at database level

- ✅ **§164.312(a)(1)** - Technical Access Controls
  - Unique user identification via `app.current_user_id`

- ✅ **§164.312(b)** - Audit Controls
  - All data access filtered through auditable RLS policies

### Audit Evidence

For compliance audits, provide:
1. This documentation
2. RLS test results (from `06 - rls_tests.sql`)
3. Query logs showing RLS context variables being set
4. Schema dump showing `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`

## Maintenance

### Adding New Tables

When adding a new tenant-scoped table:

1. **Determine scoping method**:
   - Direct: Add `organization_id` column
   - Indirect: Link via existing tenant-scoped table

2. **Enable RLS**:
   ```sql
   ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;
   ```

3. **Create policy**:
   ```sql
   CREATE POLICY new_table_isolation ON new_table
       FOR ALL
       USING (
           organization_id = current_setting('app.current_tenant_id', true)::UUID
           OR is_super_admin()
       );
   ```

4. **Add test coverage** in `06 - rls_tests.sql`

5. **Update this documentation**

### Schema Migrations

When modifying RLS policies:

1. Write forward migration (new policy)
2. Write rollback migration (drop policy, disable RLS)
3. Test both directions
4. Document changes in migration comments

## References

- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [OWASP Database Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html)

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-14 | 1.0 | Initial RLS implementation |

---

**Status**: ✅ **Production Ready**

This RLS implementation provides comprehensive tenant isolation for HIPAA compliance. All critical findings from the database review have been addressed.
