"""
Pre-migration script to identify duplicate primary providers.

Run this to audit data before applying the unique primary provider constraint.

Usage:
    cd apps/backend
    uv run python scripts/check_primary_provider_violations.py

Expected Output:
    - If violations found: Lists all (org, patient) pairs with multiple primaries
    - If no violations: Confirmation message that migration is safe

This script helps diagnose data quality issues before enforcing the constraint.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.database import engine


async def check_violations():
    """
    Query database for patients with multiple primary providers.

    Returns:
        List of violation records with org_id, patient_id, and provider list
    """
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT
                organization_id,
                patient_id,
                COUNT(*) as primary_provider_count,
                ARRAY_AGG(provider_id ORDER BY assigned_at) as provider_ids,
                ARRAY_AGG(assigned_at ORDER BY assigned_at) as assigned_dates
            FROM care_team_assignments
            WHERE is_primary_provider = TRUE
            GROUP BY organization_id, patient_id
            HAVING COUNT(*) > 1
            ORDER BY organization_id, patient_id;
        """))

        violations = result.fetchall()
        return violations


async def main():
    """Main execution function."""
    print("=" * 70)
    print("PRIMARY PROVIDER CONSTRAINT VIOLATION CHECK")
    print("=" * 70)
    print()
    print("Checking for patients with multiple primary providers...")
    print()

    try:
        violations = await check_violations()

        if violations:
            print(f"⚠️  VIOLATIONS FOUND: {len(violations)} patient(s) with duplicate primaries")
            print()
            print("-" * 70)

            for idx, v in enumerate(violations, 1):
                print(f"\nViolation #{idx}:")
                print(f"  Organization ID: {v.organization_id}")
                print(f"  Patient ID:      {v.patient_id}")
                print(f"  Primary Count:   {v.primary_provider_count}")
                print(f"  Provider IDs:    {v.provider_ids}")
                print(f"  Assigned Dates:  {v.assigned_dates}")
                print()
                print(f"  ℹ️  Migration will keep: {v.provider_ids[0]} (earliest assignment)")
                print(f"  ℹ️  Will demote to non-primary: {v.provider_ids[1:]}")

            print()
            print("-" * 70)
            print()
            print("RECOMMENDATION:")
            print("  The migration will automatically resolve these violations by:")
            print("  1. Keeping the EARLIEST assigned provider as primary (based on assigned_at)")
            print("  2. Setting is_primary_provider=FALSE for all others")
            print()
            print("  Review the violations above. If the earliest assignment is NOT the")
            print("  correct primary provider, manually update the data before migration:")
            print()
            print("  UPDATE care_team_assignments")
            print("  SET is_primary_provider = TRUE")
            print("  WHERE id = '<correct_provider_assignment_id>';")
            print()
            print("  UPDATE care_team_assignments")
            print("  SET is_primary_provider = FALSE")
            print("  WHERE organization_id = '<org_id>'")
            print("    AND patient_id = '<patient_id>'")
            print("    AND id != '<correct_provider_assignment_id>';")
            print()

            return 1  # Exit with error code
        else:
            print("✅ SUCCESS: No violations found")
            print()
            print("All patients have at most ONE primary provider.")
            print("Safe to apply the unique constraint migration.")
            print()

            return 0  # Exit with success code

    except Exception as e:
        print(f"❌ ERROR: Failed to check violations")
        print(f"   {type(e).__name__}: {e}")
        print()
        print("Ensure the database is accessible and the schema is up to date.")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
