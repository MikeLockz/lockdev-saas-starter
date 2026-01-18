import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to allow imports from agent package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from agent.adapters.linear_adapter import LinearAdapter


def main():
    # Load environment variables
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    load_dotenv(env_path)

    api_key = os.getenv("LINEAR_API_KEY")
    team_key = os.getenv("LINEAR_TEAM_KEY", "ENG")

    if not api_key:
        print("Error: LINEAR_API_KEY not found in environment variables.")
        return

    print(f"Initializing Linear Adapter for team: {team_key}")
    try:
        adapter = LinearAdapter()
    except ValueError as e:
        print(f"Error initializing adapter: {e}")
        return

    team_id = adapter.get_team_id(team_key)
    if not team_id:
        print(f"Error: Could not find team with key {team_key}")
        print("Fetching available teams...")
        query_teams = """
        query {
            teams {
                nodes {
                    id
                    key
                    name
                }
            }
        }
        """
        try:
            result = adapter._query(query_teams)
            teams = result.get("data", {}).get("teams", {}).get("nodes", [])
            print("Available teams:")
            for t in teams:
                print(f"- {t['name']} (Key: {t['key']})")
        except Exception as e:
            print(f"Failed to list teams: {e}")
        return

    # 1. Clear out all existing tickets
    print("\n--- Clearing all existing tickets ---")

    # We loop because pagination might be needed (or just query 250 at a time until empty)
    while True:
        query_all_issues = """
        query GetTeamIssues($teamId: String!) {
            team(id: $teamId) {
                issues(first: 100) {
                    nodes {
                        id
                        identifier
                        title
                    }
                }
            }
        }
        """
        result = adapter._query(query_all_issues, {"teamId": team_id})
        issues = (
            result.get("data", {}).get("team", {}).get("issues", {}).get("nodes", [])
        )

        if not issues:
            print("No issues found.")
            break

        print(f"Found {len(issues)} issues. Deleting...")
        for issue in issues:
            print(f"Deleting {issue['identifier']}: {issue['title']}")
            mutation_delete = """
            mutation DeleteIssue($id: String!) {
                issueDelete(id: $id) {
                    success
                }
            }
            """
            try:
                adapter._query(mutation_delete, {"id": issue["id"]})
                # Small delay to avoid rate limits if necessary
                # time.sleep(0.1)
            except Exception as e:
                print(f"Failed to delete {issue['identifier']}: {e}")

        # If we fetched fewer than requested, we are done
        if len(issues) < 100:
            break

    # 2. Wipe out all existing columns (Workflow States)
    print("\n--- Clearing all existing workflow states ---")

    # Fetch all states
    query_states = """
    query GetStates($teamId: String!) {
        team(id: $teamId) {
            states {
                nodes {
                    id
                    name
                    type
                }
            }
        }
    }
    """
    result = adapter._query(query_states, {"teamId": team_id})
    states = result.get("data", {}).get("team", {}).get("states", {}).get("nodes", [])

    if not states:
        print("No states found.")
    else:
        print(f"Found {len(states)} states. Deleting...")
        for state in states:
            print(f"Attempting to delete state: {state['name']} ({state['type']})")
            mutation_delete_state = """
            mutation DeleteState($id: String!) {
                workflowStateDelete(id: $id) {
                    success
                }
            }
            """
            try:
                # Note: Delete might fail if it's the last state or used by issues (deleted issues might still be linked?)
                # Actually deleted issues shouldn't block.
                res = adapter._query(mutation_delete_state, {"id": state["id"]})
                if res.get("data", {}).get("workflowStateDelete", {}).get("success"):
                    print("  Success")
                else:
                    # This happens for default states usually
                    print(
                        "  Failed (API returned false success, possibly default state)"
                    )
            except Exception as e:
                print(f"  Failed: {str(e)}")

    # 3. Create appropriate columns
    print("\n--- Creating required workflow states ---")
    adapter.ensure_workflow_states(team_key)
    print("\nValues updated successfully!")


if __name__ == "__main__":
    main()
