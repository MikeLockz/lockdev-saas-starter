from typing import Dict, Any
from tools.cmd_runner import run_command


def reviewer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs 'make check' (linting) and 'make test' (tests).
    If it fails, it reports the error.
    """
    print("🕵️ Reviewer: Running The Gauntlet (Lint → Test)...")

    # 1. Run Linting (make check)
    # This runs Ruff for backend, Biome for frontend, and pre-commit checks
    lint_result = run_command("make check")
    if not lint_result["success"]:
        print("❌ Reviewer: Lint Check Failed!")
        print(lint_result["output"][:500])  # Print first 500 chars
        return {
            "status": "failed",
            "error": f"Lint Error:\n{lint_result['output']}",
            "review_type": "lint",
        }

    print("✅ Reviewer: Lint Check Passed.")

    # 2. Run Tests (make test)
    # This runs pytest for backend and vitest for frontend
    test_result = run_command("make test")
    if not test_result["success"]:
        print("❌ Reviewer: Tests Failed!")
        print(test_result["output"][:500])
        return {
            "status": "failed",
            "error": f"Test Error:\n{test_result['output']}",
            "review_type": "test",
        }

    print("✅ Reviewer: Tests Passed.")

    # Move to Human: Final Approval if we have a ticket ID
    ticket_id = state.get("ticket_id")
    if ticket_id:
        from tools.linear_adapter import update_issue_status

        print("📤 Reviewer: Moving ticket to Human: Final Approval...")
        if update_issue_status(ticket_id, "Human: Final Approval"):
            print("✅ Reviewer: Ticket moved successfully.")
        else:
            print("⚠️ Reviewer: Failed to move ticket.")

    return {"status": "approved", "error": None}
