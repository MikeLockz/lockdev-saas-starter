import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_audit_trigger_exists(db_session):
    """Verify audit trigger function exists"""
    result = await db_session.execute(
        text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_proc 
            WHERE proname = 'audit_trigger_func'
        )
    """)
    )
    exists = result.scalar()
    assert exists, "audit_trigger_func should exist"


@pytest.mark.asyncio
async def test_audit_triggers_on_tables(db_session):
    """Verify triggers are attached to tables"""
    result = await db_session.execute(
        text("""
        SELECT tgname, tgrelid::regclass::text as table_name
        FROM pg_trigger
        WHERE tgname LIKE 'audit_trigger_%'
        ORDER BY table_name
    """)
    )
    triggers = result.fetchall()

    trigger_tables = {row[1] for row in triggers}
    expected_tables = {"patients", "organization_memberships", "proxies", "consent_documents", "user_consents"}

    assert expected_tables.issubset(trigger_tables), f"Expected triggers on {expected_tables}, found {trigger_tables}"


@pytest.mark.asyncio
async def test_rls_enabled(db_session):
    """Verify RLS is enabled on sensitive tables"""
    result = await db_session.execute(
        text("""
        SELECT tablename, rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public' 
        AND tablename IN ('patients', 'proxies', 'organization_memberships', 'audit_logs')
        ORDER BY tablename
    """)
    )
    tables = result.fetchall()

    for table_name, rls_enabled in tables:
        assert rls_enabled, f"RLS should be enabled on {table_name}"


@pytest.mark.asyncio
async def test_rls_policies_exist(db_session):
    """Verify RLS policies exist"""
    result = await db_session.execute(
        text("""
        SELECT tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
        ORDER BY tablename, policyname
    """)
    )
    policies = result.fetchall()

    policy_names = {row[1] for row in policies}
    expected_policies = {
        "audit_logs_insert",
        "audit_logs_select",
        "org_members_isolation",
        "patient_isolation",
        "proxy_user_isolation",
    }

    assert expected_policies.issubset(policy_names), f"Expected policies {expected_policies}, found {policy_names}"
