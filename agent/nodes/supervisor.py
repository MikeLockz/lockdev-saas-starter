from typing import Dict, Any
from tools.linear_adapter import fetch_issues, update_issue_status


def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Polls Linear for 'Ready for AI' tickets.
    If found, picks the first one, marks it 'In Progress', and sets the task.
    """
    print("👀 Supervisor: Polling Linear for work...")

    issues = fetch_issues("AI: Ready to Implement")

    if not issues:
        print("💤 Supervisor: No work found. Resting.")
        return {"task": None, "status": "idle"}

    # Pick the first one
    issue = issues[0]
    issue_id = issue["id"]
    title = issue["title"]
    description = issue["description"] or ""

    print(f"🎯 Supervisor: Found Ticket {issue['identifier']}: {title}")

    # Update status to 'In Progress' to claim it
    success = update_issue_status(issue_id, "AI: In Progress")
    if success:
        print(f"✅ Supervisor: Marked {issue['identifier']} as 'AI: In Progress'")
    else:
        print(
            f"⚠️ Supervisor: Failed to update status for {issue['identifier']}, but proceeding anyway."
        )

    full_task_description = f"Title: {title}\n\nDescription:\n{description}"

    return {"task": full_task_description, "ticket_id": issue_id, "status": "working"}
