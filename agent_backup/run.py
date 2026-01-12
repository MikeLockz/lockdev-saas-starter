import os
import argparse
import sys
from dotenv import load_dotenv

from graph import app
from nodes.reviewer import reviewer_node
from nodes.pm import pm_node
from nodes.staff_engineer import staff_engineer_node
from nodes.spec_reviewer import spec_reviewer_node

# Load Keys FIRST, before modules use them (though many load at runtime)
load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Run the AI Agent Workflow")
    parser.add_argument(
        "--gauntlet", action="store_true", help="Run only the Gauntlet (Reviewer/Tests)"
    )
    parser.add_argument(
        "--pm-only",
        action="store_true",
        help="Run only the PM agent (refine Backlog tickets)",
    )
    parser.add_argument(
        "--staff-only",
        action="store_true",
        help="Run only the Staff Engineer agent (break down Spec Backlog tickets)",
    )
    parser.add_argument(
        "--spec-review-only",
        action="store_true",
        help="Run only the Spec Reviewer agent (review Spec Review tickets)",
    )
    parser.add_argument(
        "--skip-pm", action="store_true", help="Skip PM agent, only run dev workflow"
    )
    args = parser.parse_args()

    if args.gauntlet:
        print("🚀 Starting Gauntlet Mode (Reviewer)...")
        result = reviewer_node({})
        if result.get("status") == "failed":
            print(f"\n❌ Gauntlet Failed: {result.get('error')}")
            sys.exit(1)
        else:
            print("\n✅ Gauntlet Passed!")
        return

    # --- Check Required Keys ---
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY is missing in .env")
        exit(1)

    if not os.getenv("LINEAR_API_KEY"):
        print("❌ Error: LINEAR_API_KEY is missing in .env")
        exit(1)

    # --- Phase 1: PM Agent (Refine Backlog tickets) ---
    if not args.skip_pm:
        print("\n" + "=" * 50)
        print("📋 PHASE 1: Product Manager Agent")
        print("=" * 50)
        pm_result = pm_node({})

        if args.pm_only:
            print("\n✅ PM PHASE COMPLETE!")
            print(f"Tickets processed: {pm_result.get('pm_processed', 0)}")
            return

    # --- Phase 1.5: Staff Engineer Agent (Break down Spec Backlog tickets) ---
    if not args.skip_pm:  # Staff Engineer runs after PM, in same flow
        print("\n" + "=" * 50)
        print("🔧 PHASE 1.5: Staff Software Engineer Agent")
        print("=" * 50)
        staff_result = staff_engineer_node({})

        if args.staff_only:
            print("\n✅ STAFF ENGINEER PHASE COMPLETE!")
            print(f"Tickets processed: {staff_result.get('staff_processed', 0)}")
            return

    # --- Phase 1.75: Spec Reviewer Agent (Review sub-tickets for conformance) ---
    if not args.skip_pm:
        print("\n" + "=" * 50)
        print("🔍 PHASE 1.75: Spec Reviewer Agent")
        print("=" * 50)
        spec_result = spec_reviewer_node({})

        if args.spec_review_only:
            print("\n✅ SPEC REVIEW PHASE COMPLETE!")
            print(f"Tickets reviewed: {spec_result.get('spec_reviewed', 0)}")
            return

    # --- Phase 2: Dev Workflow (Ready for AI -> Code -> Review) ---
    print("\n" + "=" * 50)
    print("🚀 PHASE 2: Development Workflow")
    print("=" * 50)
    print("👀 Polling Linear for 'AI: Ready to Implement' tickets...")

    # Start with empty inputs, Supervisor will populate
    inputs = {}
    # Set recursion limit to 20 to allow for 3-4 repair loops
    result = app.invoke(inputs, {"recursion_limit": 20})

    print("\n✅ WORKFLOW COMPLETE!")
    print(f"Final Status: {result.get('status', 'Unknown')}")
    if result.get("task"):
        print(f"Processed Task: {result['task'][:50]}...")
    if "contract_path" in result:
        print(f"Contract: {result['contract_path']}")


if __name__ == "__main__":
    main()
