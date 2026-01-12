import requests
from tools.linear_adapter import update_issue_status, get_headers, LINEAR_API_URL


def reset_ticket():
    # 1. Fetch In Progress tickets
    print("Fetching 'AI: In Progress' tickets...")

    # We need to manually query because fetch_issues defaults to Ready to Implement
    query = """
    query Issues($filter: IssueFilter) {
      issues(filter: $filter) {
        nodes {
          id
          identifier
          title
          state {
            name
          }
        }
      }
    }
    """

    variables = {"filter": {"state": {"name": {"eq": "AI: In Progress"}}}}

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query, "variables": variables},
    )

    data = response.json()
    issues = data.get("data", {}).get("issues", {}).get("nodes", [])

    target_issue = None
    for issue in issues:
        if "Create usePatientSearch hook" in issue["title"]:
            target_issue = issue
            break

    if not target_issue:
        print(
            "Could not find 'Create usePatientSearch hook' ticket in 'AI: In Progress'."
        )
        # Fallback: pick the first one if any exist
        if issues:
            target_issue = issues[0]
            print(f"Falling back to: {target_issue['title']}")
        else:
            print("No 'AI: In Progress' tickets found.")
            return

    print(
        f"Resetting ticket {target_issue['identifier']}: {target_issue['title']} to 'AI: Ready to Implement'..."
    )
    success = update_issue_status(target_issue["id"], "AI: Ready to Implement")

    if success:
        print("✅ Successfully reset ticket status.")
    else:
        print("❌ Failed to reset ticket status.")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    reset_ticket()
