import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.file_io import read_project_rules
from tools.linear_adapter import fetch_issues, create_sub_issue, update_issue_status
from config import AGENT_CONFIG
from typing import Dict, Any

# Using Gemini for Staff Engineer reasoning
llm = ChatGoogleGenerativeAI(
    model=AGENT_CONFIG.get("staff_engineer", {}).get("model", "gemini-2.0-flash"),
    temperature=AGENT_CONFIG.get("staff_engineer", {}).get("temperature", 0.3),
)

SYSTEM_PROMPT = """You are a Senior Staff Software Engineer with expertise in breaking down features into well-defined, implementable tasks.

Your job is to analyze a fully-specified ticket (with user story and acceptance criteria) and decompose it into discrete sub-tickets that can be independently implemented and tested.

## CRITICAL: Apply Project Rules

You will receive PROJECT RULES that define:
- Tech stack and frameworks (FastAPI, SQLAlchemy, React, TanStack, etc.)
- File organization and code locations (where to put models, routes, components, hooks)
- Naming conventions (hooks, query keys, API URLs)
- Database conventions (ULID for IDs, soft deletes, multi-tenancy)
- Testing requirements (pytest, vitest, Playwright)
- Makefile commands (ALWAYS reference these, never raw npm/pip commands)

You MUST apply these rules when generating sub-tickets:
- Reference correct file paths (e.g., `apps/backend/src/models/`, `apps/frontend/src/hooks/`)
- Use correct naming patterns (e.g., `useEntity`, `useCreateEntity` for hooks)
- Specify correct test frameworks (pytest for backend, vitest for frontend, Playwright for E2E)
- Include `make check` and `make test` in acceptance criteria
- Ensure database schemas use ULID, soft deletes, and org-scoping

## Sub-Ticket Format

For each sub-ticket, you MUST provide:
1. A clear, concise title
2. A description with:
   - What needs to be implemented (with specific file paths per project rules)
   - Acceptance Criteria (specific, testable checkboxes)
   - Test Criteria:
     - Unit Tests: What functions/methods to test (pytest for backend, vitest for frontend)
     - Integration Tests: What API/service boundaries to test
     - E2E Tests: What user flows to test in Playwright (or "N/A" if not UI-facing)

## CRITICAL OUTPUT FORMAT

You MUST output valid JSON only. No markdown, no explanation. Just a JSON array:

```json
[
  {
    "title": "Implement User model and migrations",
    "description": "## What to Implement\\nCreate the SQLAlchemy model in `apps/backend/src/models/user.py`...\\n\\n## Acceptance Criteria\\n- [ ] User model exists with ULID primary key\\n- [ ] Model uses soft delete (deleted_at column)\\n- [ ] Alembic migration created via `make migrate`\\n- [ ] `make check` passes\\n\\n## Test Criteria\\n### Unit Tests (pytest)\\n- Test model field validation\\n- Test default values\\n\\n### Integration Tests (pytest)\\n- Test CRUD operations via repository\\n\\n### E2E Tests\\nN/A (backend only)"
  },
  {
    "title": "Create User API endpoints",
    "description": "## What to Implement\\nCreate endpoints in `apps/backend/src/api/v1/endpoints/users.py`...\\n\\n## Acceptance Criteria\\n- [ ] GET /api/v1/organizations/{org_id}/users returns paginated list\\n- [ ] All endpoints require auth (Firebase JWT)\\n- [ ] `make check` and `make test-backend` pass\\n\\n## Test Criteria\\n### Unit Tests (pytest)\\n- Test response serialization\\n\\n### Integration Tests (pytest)\\n- Test full request/response cycle\\n- Test authorization checks\\n\\n### E2E Tests\\nN/A (API only)"
  },
  {
    "title": "Create useUsers hook",
    "description": "## What to Implement\\nCreate TanStack Query hook in `apps/frontend/src/hooks/useUsers.ts`...\\n\\n## Acceptance Criteria\\n- [ ] Hook follows naming convention: useUsers, useUserById, useCreateUser\\n- [ ] Uses query key pattern ['users', { orgId }]\\n- [ ] Uses @/ path aliases for imports\\n- [ ] `make check` passes\\n\\n## Test Criteria\\n### Unit Tests (vitest)\\n- Test hook returns correct data shape\\n- Test loading/error states\\n\\n### Integration Tests\\nN/A (use E2E)\\n\\n### E2E Tests (Playwright)\\n- Test user list renders after login"
  }
]
```

## Guidelines
- Break work into logical, independently-testable units
- Backend before frontend (dependencies first)
- Database migrations as separate tickets when schema changes
- Each sub-ticket should be completable in 1-4 hours
- Always reference project-specific file paths and conventions
- Include `make check` in acceptance criteria for all tickets
"""


def staff_engineer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Staff Software Engineer agent that:
    1. Polls Linear for 'Spec Backlog' tickets (human-approved specs)
    2. Breaks down features into sub-tickets
    3. Each sub-ticket has acceptance criteria and test criteria
    4. Creates sub-issues in Linear
    5. Moves parent to 'Ready for AI' for implementation
    """
    print("🔧 Staff Engineer: Looking for approved specs to break down...")

    issues = fetch_issues("AI: Spec Backlog")

    if not issues:
        print("💤 Staff Engineer: No approved specs found. Resting.")
        return {"staff_status": "idle", "staff_processed": 0}

    project_rules = read_project_rules()
    processed_count = 0

    for issue in issues:
        issue_id = issue["id"]
        identifier = issue["identifier"]
        title = issue["title"]
        description = issue.get("description") or ""

        print(f"📋 Staff Engineer: Breaking down {identifier}: {title}")

        prompt = f"""
Parent Ticket: {identifier}
Title: {title}

## Full Requirements (from Product Manager):
{description}

---

## PROJECT RULES (MUST APPLY):
{project_rules}

---

## Instructions:
1. Read the requirements above carefully
2. Apply ALL project rules when generating sub-tickets:
   - Use correct file paths from project structure
   - Reference correct test frameworks (pytest/vitest/Playwright)
   - Include `make check` and `make test` in acceptance criteria
   - Follow naming conventions for hooks, APIs, and models
   - Use ULID for IDs, soft deletes, and org-scoping in DB models
3. Break into discrete, independently-testable sub-tickets
4. Output ONLY valid JSON array, no other text
"""

        response = llm.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
        )

        content = response.content
        if isinstance(content, list):
            content = "".join([str(x) for x in content])
        content = content.strip()

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        if json_match:
            content = json_match.group(1).strip()

        try:
            sub_tickets = json.loads(content)
        except json.JSONDecodeError as e:
            print(
                f"❌ Staff Engineer: Failed to parse sub-tickets for {identifier}: {e}"
            )
            print(f"   Raw response: {content[:200]}...")
            continue

        if not isinstance(sub_tickets, list) or len(sub_tickets) == 0:
            print(f"⚠️ Staff Engineer: No valid sub-tickets generated for {identifier}")
            continue

        # Create sub-issues in Linear
        created_count = 0
        for i, ticket in enumerate(sub_tickets, 1):
            sub_title = ticket.get("title", f"Sub-task {i}")
            sub_description = ticket.get("description", "")

            result = create_sub_issue(issue_id, sub_title, sub_description)
            if result:
                sub_issue_id, sub_identifier = result
                print(f"  ✅ Created {sub_identifier}: {sub_title}")

                # Move sub-issue to Spec Review
                if update_issue_status(sub_issue_id, "AI: Spec Improve"):
                    print(f"     📤 Moved {sub_identifier} to AI: Spec Improve")

                created_count += 1
            else:
                print(f"  ❌ Failed to create: {sub_title}")

        print(
            f"📋 Staff Engineer: Created {created_count}/{len(sub_tickets)} sub-tickets for {identifier}"
        )

        # Move parent ticket to In Progress so Supervisor doesn't pick it up
        if created_count > 0:
            status_success = update_issue_status(issue_id, "AI: In Progress")
            if status_success:
                print(f"📤 Staff Engineer: Moved {identifier} to AI: In Progress")
            else:
                print(
                    f"⚠️ Staff Engineer: Could not move {identifier} to AI: In Progress"
                )

            processed_count += 1

    print(f"🔧 Staff Engineer: Processed {processed_count} tickets")
    return {"staff_status": "complete", "staff_processed": processed_count}
