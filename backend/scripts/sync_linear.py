import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List

import httpx

# =============================================================================
# CONFIGURATION & UTILS
# =============================================================================

ROOT_DIR = Path(__file__).parent.parent.parent
DOCS_DIR = ROOT_DIR / "docs" / "implementation-plan"
ENV_FILE = ROOT_DIR / ".env"

def load_env():
    """Simple .env loader"""
    if not ENV_FILE.exists():
        print(f"Warning: .env file not found at {ENV_FILE}")
        return

    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                os.environ[key] = value

load_env()

LINEAR_API_KEY = os.getenv("LINEAR_API_KEY")
LINEAR_API_URL = "https://api.linear.app/graphql"

if not LINEAR_API_KEY:
    print("Error: LINEAR_API_KEY not found in .env")
    sys.exit(1)

HEADERS = {
    "Authorization": LINEAR_API_KEY,
    "Content-Type": "application/json",
}

# =============================================================================
# LINEAR CLIENT
# =============================================================================

async def linear_query(query: str, variables: dict = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            LINEAR_API_URL,
            headers=HEADERS,
            json={"query": query, "variables": variables},
        )
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            sys.exit(1)
        
        data = response.json()
        if "errors" in data:
            print(f"GraphQL Errors: {data['errors']}")
            sys.exit(1)
            
        return data["data"]

# =============================================================================
# PARSERS
# =============================================================================

def parse_epic(file_path: Path) -> dict:
    content = file_path.read_text()
    # Extract title from first line "# Epic X: Name"
    title_match = re.search(r"^# (Epic \d+: .+?)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.parent.name
    
    # Extract description (User Story)
    story_match = re.search(r"\*\*User Story:\*\* (.*?)\n", content)
    description = story_match.group(1) if story_match else "Imported from implementation plan."
    
    return {
        "title": title,
        "description": description,
        "path": file_path
    }

def parse_story(file_path: Path) -> dict:
    content = file_path.read_text()
    # Extract title "# Story X.X: Name"
    title_match = re.search(r"^# (Story [\d\.]+: .+?)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.name
    
    # Extract status
    status_match = re.search(r"## Status\n- \[(x| )\].*?\*\*", content)
    is_done = status_match.group(1) == "x" if status_match else False
    
    # Extract full body for description
    description = f"**Source:** `{file_path.relative_to(ROOT_DIR)}`\n\n{content}"
    
    return {
        "title": title,
        "description": description,
        "is_done": is_done
    }

# =============================================================================
# MAIN SYNC LOGIC
# =============================================================================

async def main():
    print("🚀 Starting Linear Sync...")
    
    # 1. Get Viewer & Team
    print("Creating connection to Linear...")
    viewer_query = """
    query {
        viewer { id name }
        teams { nodes { id name key } }
    }
    """
    data = await linear_query(viewer_query)
    viewer = data["viewer"]
    teams = data["teams"]["nodes"]
    
    print(f"Authenticated as: {viewer['name']}")
    
    if not teams:
        print("Error: No teams found in Linear. Please create a team first.")
        sys.exit(1)
        
    # Auto-select first team or ask (simplified to first for automation)
    team = teams[0]
    print(f"Using Team: {team['name']} ({team['key']})")
    
    # 2. Find or Create Project
    project_name = "Lockdev SaaS Implementation"
    print(f"Checking for project: {project_name}...")
    
    # Simplified: search for project by name (Linear doesn't have simple search in basic query, 
    # so we'll just try to create it or assume unique for this script run)
    # Actually, let's create it. If it duplicates, user can delete. 
    # Proper way: list projects and check name.
    
    projects_query = """
    query {
        projects { nodes { id name } }
    }
    """
    p_data = await linear_query(projects_query)
    existing_project = next((p for p in p_data["projects"]["nodes"] if p["name"] == project_name), None)
    
    if existing_project:
        project_id = existing_project["id"]
        print(f"Found existing project: {project_id}")
    else:
        create_project_mutation = """
        mutation ProjectCreate($input: ProjectCreateInput!) {
            projectCreate(input: $input) {
                project { id }
            }
        }
        """
        p_res = await linear_query(create_project_mutation, {
            "input": {
                "name": project_name,
                "teamIds": [team["id"]],
                "state": "planned"
            }
        })
        project_id = p_res["projectCreate"]["project"]["id"]
        print(f"Created Project: {project_id}")

    # 3. Iterate Epics
    epic_dirs = sorted([d for d in DOCS_DIR.iterdir() if d.is_dir() and d.name.startswith("epic-")])
    
    for epic_dir in epic_dirs:
        index_file = epic_dir / "index.md"
        if not index_file.exists():
            continue
            
        epic_data = parse_epic(index_file)
        print(f"\nProcessing Epic: {epic_data['title']}")
        
        # Treat Docs "Epic" as a Parent Issue in the Linear Project
        # Linear doesn't have a separate "Epic" entity in this context (often Projects are Epics).
        # Since we have a master Project, we'll make these Parent Issues.
        
        create_parent_issue_mutation = """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                issue { id identifier }
            }
        }
        """
        
        epic_input = {
            "teamId": team["id"],
            "projectId": project_id,
            "title": epic_data["title"],
            "description": epic_data["description"]
        }
        
        e_res = await linear_query(create_parent_issue_mutation, {"input": epic_input})
        linear_epic_id = e_res["issueCreate"]["issue"]["id"]
        linear_epic_identifier = e_res["issueCreate"]["issue"]["identifier"]
        print(f"  -> Created Epic (Parent Issue): {linear_epic_identifier}")
        
        # 4. Process Stories
        story_files = sorted([f for f in epic_dir.iterdir() if f.name.startswith("story-") and f.suffix == ".md"])
        
        for story_file in story_files:
            story_data = parse_story(story_file)
            print(f"  -> Processing Story: {story_data['title']}")
            
            # Map state
            # state_name = "Done" if story_data["is_done"] else "Todo"
            
            create_issue_mutation = """
            mutation IssueCreate($input: IssueCreateInput!) {
                issueCreate(input: $input) {
                    issue { id identifier }
                }
            }
            """
            
            i_input = {
                "teamId": team["id"],
                "projectId": project_id, 
                "title": story_data["title"],
                "description": story_data["description"],
                "parentId": linear_epic_id
            }
            
            i_res = await linear_query(create_issue_mutation, {"input": i_input})
            issue = i_res["issueCreate"]["issue"]
            print(f"     -> Created Issue: {issue['identifier']}")
            
            if story_data["is_done"]:
                print(f"     -> Note: Story is marked DONE in docs. Please update status in Linear manually.")

    print("\n✅ Sync Complete!")

if __name__ == "__main__":
    asyncio.run(main())
