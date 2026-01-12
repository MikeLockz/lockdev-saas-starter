import os
import requests
from typing import List, Dict, Optional

LINEAR_API_URL = "https://api.linear.app/graphql"


def get_headers():
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        raise ValueError("LINEAR_API_KEY not found in environment variables")
    return {"Content-Type": "application/json", "Authorization": api_key}


def list_states() -> List[str]:
    query = """
    query {
      workflowStates {
        nodes {
          name
          id
        }
      }
    }
    """
    response = requests.post(
        LINEAR_API_URL, headers=get_headers(), json={"query": query}
    )
    if response.status_code == 200:
        states = (
            response.json().get("data", {}).get("workflowStates", {}).get("nodes", [])
        )
        return [s["name"] for s in states]
    return []


def fetch_issues(status_name: str = "AI: Ready to Implement") -> List[Dict]:
    """
    Fetches issues with a specific status name.
    """
    query = """
    query Issues($filter: IssueFilter) {
      issues(filter: $filter) {
        nodes {
          id
          identifier
          title
          description
          state {
            name
          }
          assignee {
            name
          }
          attachments {
            nodes {
              id
              title
              subtitle
              url
              sourceType
              metadata
            }
          }
        }
      }
    }
    """

    variables = {"filter": {"state": {"name": {"eq": status_name}}}}

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query, "variables": variables},
    )

    if response.status_code != 200:
        print(f"Error fetching issues: {response.text}")
        return []

    data = response.json()
    if "errors" in data:
        print(f"GraphQL Errors: {data['errors']}")
        return []

    issues = data.get("data", {}).get("issues", {}).get("nodes", [])
    if not issues:
        # Debug: check what states actually exist
        print(f"🔍 Linear Adapter: No issues found for status '{status_name}'.")

        # New Debug: Print all active issues to see where they are
        all_query = """{ issues { nodes { title state { name } } } }"""
        all_resp = requests.post(
            LINEAR_API_URL, headers=get_headers(), json={"query": all_query}
        )
        if all_resp.status_code == 200:
            all_issues = (
                all_resp.json().get("data", {}).get("issues", {}).get("nodes", [])
            )
            print(
                f"📍 Current issues in Linear: {[(i['title'], i['state']['name']) for i in all_issues]}"
            )

        print(f"📌 Available states: {list_states()}")

    return issues


def update_issue_status(issue_id: str, new_status_name: str) -> bool:
    """
    Updates the status of an issue.
    First, we need to find the state ID for the new status name in the issue's team.
    For simplicity, we'll search for the state ID globally or assume we can get it from the issue context if we had it.

    Actually, to update state, we need the State ID.
    Let's add a helper to find State ID by name for a given team, or just search workflow states.
    """

    # First, find the State ID for the desired status name.
    # This is a bit complex in Linear as states are per-team.
    # We might need to look up the issue to get its team, then find the state in that team.

    # 1. Get Issue's Team ID
    team_query = """
    query Issue($id: String!) {
      issue(id: $id) {
        team {
          id
          states {
            nodes {
              id
              name
            }
          }
        }
      }
    }
    """

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": team_query, "variables": {"id": issue_id}},
    )

    if response.status_code != 200:
        return False

    data = response.json()
    team_data = data.get("data", {}).get("issue", {}).get("team", {})
    states = team_data.get("states", {}).get("nodes", [])

    target_state_id = next(
        (s["id"] for s in states if s["name"] == new_status_name), None
    )

    if not target_state_id:
        print(f"State '{new_status_name}' not found for the issue's team.")
        return False

    # 2. Update the issue
    mutation = """
    mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue {
          id
          state {
            name
          }
        }
      }
    }
    """

    variables = {"id": issue_id, "input": {"stateId": target_state_id}}

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": mutation, "variables": variables},
    )

    if response.status_code != 200:
        print(f"Failed to update issue: {response.text}")
        return False

    return response.json().get("data", {}).get("issueUpdate", {}).get("success", False)


def update_issue_description(issue_id: str, new_description: str) -> bool:
    """
    Updates the description of an issue with the fleshed-out user story.
    """
    mutation = """
    mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        success
        issue {
          id
          description
        }
      }
    }
    """

    variables = {"id": issue_id, "input": {"description": new_description}}

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": mutation, "variables": variables},
    )

    if response.status_code != 200:
        print(f"Failed to update issue description: {response.text}")
        return False

    return response.json().get("data", {}).get("issueUpdate", {}).get("success", False)


def get_team_id(issue_id: str) -> Optional[str]:
    """
    Fetches the team ID for a given issue.
    Required for creating sub-issues.
    """
    query = """
    query Issue($id: String!) {
      issue(id: $id) {
        team {
          id
        }
      }
    }
    """

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query, "variables": {"id": issue_id}},
    )

    if response.status_code != 200:
        print(f"Failed to get team ID: {response.text}")
        return None

    return response.json().get("data", {}).get("issue", {}).get("team", {}).get("id")


def create_sub_issue(parent_id: str, title: str, description: str) -> Optional[tuple]:
    """
    Creates a sub-issue (child issue) under a parent issue.
    Returns a tuple of (issue_id, identifier) if successful, e.g., ("uuid", "PROJ-123").
    """
    # First, get the team ID from the parent
    team_id = get_team_id(parent_id)
    if not team_id:
        print(f"Cannot create sub-issue: failed to get team ID for parent {parent_id}")
        return None

    mutation = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
        }
      }
    }
    """

    variables = {
        "input": {
            "teamId": team_id,
            "parentId": parent_id,
            "title": title,
            "description": description,
        }
    }

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": mutation, "variables": variables},
    )

    if response.status_code != 200:
        print(f"Failed to create sub-issue: {response.text}")
        return None

    data = response.json()
    if "errors" in data:
        print(f"GraphQL Errors creating sub-issue: {data['errors']}")
        return None

    result = data.get("data", {}).get("issueCreate", {})
    if result.get("success"):
        issue = result.get("issue", {})
        return (issue.get("id"), issue.get("identifier"))

    return None


def fetch_parent_issue(issue_id: str) -> Optional[Dict]:
    """Fetches the parent issue details."""
    query = """
    query Issue($id: String!) {
      issue(id: $id) {
        parent {
          id
          identifier
          title
          description
          state {
            name
          }
        }
      }
    }
    """

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query, "variables": {"id": issue_id}},
    )

    if response.status_code != 200:
        return None

    return response.json().get("data", {}).get("issue", {}).get("parent")


def fetch_sub_issues(parent_id: str) -> List[Dict]:
    """Fetches all sub-issues for a parent."""
    query = """
    query Issue($id: String!) {
      issue(id: $id) {
        children {
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
    }
    """

    response = requests.post(
        LINEAR_API_URL,
        headers=get_headers(),
        json={"query": query, "variables": {"id": parent_id}},
    )

    if response.status_code != 200:
        return []

    return (
        response.json()
        .get("data", {})
        .get("issue", {})
        .get("children", {})
        .get("nodes", [])
    )


if __name__ == "__main__":
    # Test
    try:
        issues = fetch_issues()
        print(f"Found {len(issues)} issues.")
        for issue in issues:
            print(f"- {issue['identifier']}: {issue['title']}")
    except Exception as e:
        print(f"Test failed: {e}")
