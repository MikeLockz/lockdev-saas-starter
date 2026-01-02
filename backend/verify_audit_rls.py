#!/usr/bin/env python3
"""Manual verification script for Audit & RLS migration"""
import asyncio
import asyncpg

async def verify_migration():
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        user='app',
        password='app_password',
        database='app_db'
    )
    
    print("✓ Connected to database\n")
    
    # Check function exists
    result = await conn.fetchval("""
        SELECT EXISTS (
            SELECT 1 FROM pg_proc 
            WHERE proname = 'audit_trigger_func'
        )
    """)
    print(f"{'✓' if result else '✗'} Audit trigger function exists: {result}")
    
    # Check triggers
    triggers = await conn.fetch("""
        SELECT tgname, tgrelid::regclass::text as table_name
        FROM pg_trigger
        WHERE tgname LIKE 'audit_trigger_%'
        ORDER BY table_name
    """)
    print(f"\n✓ Found {len(triggers)} audit triggers:")
    for trigger in triggers:
        print(f"  - {trigger['tgname']} on {trigger['table_name']}")
    
    # Check RLS enabled
    rls_tables = await conn.fetch("""
        SELECT tablename, rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public' 
        AND tablename IN ('patients', 'proxies', 'organization_memberships', 'audit_logs')
        ORDER BY tablename
    """)
    print(f"\n✓ RLS Status:")
    for row in rls_tables:
        status = '✓' if row['rowsecurity'] else '✗'
        print(f"  {status} {row['tablename']}: {row['rowsecurity']}")
    
    # Check policies
    policies = await conn.fetch("""
        SELECT tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
        ORDER BY tablename, policyname
    """)
    print(f"\n✓ Found {len(policies)} RLS policies:")
    for policy in policies:
        print(f"  - {policy['policyname']} on {policy['tablename']}")
    
    await conn.close()
    print("\n✓ Verification complete!")

if __name__ == '__main__':
    asyncio.run(verify_migration())
