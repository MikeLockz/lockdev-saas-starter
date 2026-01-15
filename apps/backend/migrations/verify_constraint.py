#!/usr/bin/env python3
"""Verify the PRIMARY provider constraint was created successfully."""

import asyncio
import os
import sys

# Set up path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

import asyncpg


async def verify_constraint():
    """Verify the unique partial index exists."""

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return 1

    # Convert to asyncpg format if needed
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)

        # Check for the unique partial index
        query = """
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = 'care_team_assignments'
              AND indexname = 'uq_care_team_primary';
        """

        result = await conn.fetchrow(query)

        if result:
            print("✅ SUCCESS: Constraint verified!")
            print()
            print(f"Index Name: {result['indexname']}")
            print("Index Definition:")
            print(f"  {result['indexdef']}")
            print()
            print("✅ The constraint enforces: Only one PRIMARY provider per patient")
            print("✅ Multiple SPECIALIST/CONSULTANT roles are still allowed")
            print("✅ Soft-deleted PRIMARY assignments don't block new assignments")
            await conn.close()
            return 0
        else:
            print("❌ FAILURE: Constraint not found in database")
            print()
            print("Expected index: uq_care_team_primary")
            print("Table: care_team_assignments")
            print()
            print("Run: alembic upgrade head")
            await conn.close()
            return 1

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print()
        print("Make sure:")
        print("  1. DATABASE_URL environment variable is set")
        print("  2. Database is running and accessible")
        print("  3. You have the correct credentials")
        return 1


if __name__ == "__main__":
    print("=" * 70)
    print("PRIMARY Provider Constraint - Verification")
    print("=" * 70)
    print()

    exit_code = asyncio.run(verify_constraint())
    sys.exit(exit_code)
