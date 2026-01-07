from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.file_io import read_project_rules
from tools.linear_adapter import fetch_issues, update_issue_status
from config import AGENT_CONFIG
from typing import Dict, Any

# Using Gemini for Spec Reviewer
llm = ChatGoogleGenerativeAI(
    model=AGENT_CONFIG.get("spec_reviewer", {}).get("model", "gemini-2.0-flash"),
    temperature=AGENT_CONFIG.get("spec_reviewer", {}).get("temperature", 0.2),
)

SYSTEM_PROMPT = """You are a Senior Staff Engineer acting as Technical Spec Reviewer. Your job is to ensure sub-issues are compliant with the project rules and ready for implementation.

## Your Responsibilities:
1. Review each sub-issue against the project rules
2. Identify any violations or issues
3. Provide corrections to make sub-issues compliant

## Project Rules Compliance Checks:
- **File Paths**: Must match the project structure (apps/backend/src/, apps/frontend/src/, etc.)
- **Commands**: Must use Makefile commands (make check, make test, make migrate, etc.), NEVER raw npx/pnpm/uv/docker commands
- **Database**: Must use ULID for IDs, soft deletes (deleted_at), org-scoped queries
- **API**: Must follow /api/v1/ URL structure with proper auth patterns
- **Frontend**: Must use @/ path aliases, TanStack patterns for hooks
- **Testing**: Must reference correct frameworks (pytest for backend, vitest for frontend, Playwright for E2E)
- **HIPAA**: Must not log PHI, must include audit logging for data mutations

## Output Format:
Respond with a JSON object:
```json
{
  "status": "APPROVED" | "NEEDS_FIXES",
  "issues_found": ["list of issues if any"],
  "corrections": [
    {
      "action": "ADD" | "REMOVE" | "FIX",
      "target": "what to target (e.g., 'acceptance criteria', 'file path', 'sub-issue title')",
      "original": "original text if fixing",
      "correction": "the corrected text or new content to add",
      "reason": "brief explanation"
    }
  ],
  "revised_description": "The full corrected description if fixes were needed, or null if approved as-is"
}
```

## Important:
- Be thorough but pragmatic—fix real issues, don't nitpick
- If file paths don't match project structure, correct them
- If commands use npx/pnpm directly, replace with make targets
- If acceptance criteria miss `make check` or `make test`, add them
- Ensure sub-issues are actionable and specific
"""


def spec_reviewer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Senior Staff Engineer Spec Reviewer that:
    1. Polls Linear for 'Spec Review' tickets
    2. Reviews sub-issues against project_rules.md
    3. Fixes non-compliant sub-issues (add/remove/correct)
    4. Moves reviewed tickets to 'Human Review'
    """
    import json
    from tools.linear_adapter import update_issue_description

    print("🔍 Senior Staff Engineer: Reviewing specs for compliance...")

    issues = fetch_issues("AI: Spec Improve")

    if not issues:
        print("💤 Spec Reviewer: No tickets to review. Resting.")
        return {"spec_review_status": "idle", "spec_reviewed": 0}

    project_rules = read_project_rules()
    reviewed_count = 0
    fixed_count = 0

    for issue in issues:
        issue_id = issue["id"]
        identifier = issue["identifier"]
        title = issue["title"]
        description = issue.get("description") or ""

        # Skip if no description
        if not description.strip():
            print(f"⏭️  Spec Reviewer: {identifier} has no description. Skipping.")
            continue

        print(f"🔍 Reviewing {identifier}: {title}")

        prompt = f"""
Review this ticket and its sub-issues for compliance with project rules.

## Ticket: {identifier} - {title}

## Description:
{description}

## Project Rules (MUST be followed):
{project_rules}

Review the ticket description and any sub-issues. Check for:
1. Correct file paths (apps/backend/src/, apps/frontend/src/)
2. Use of Makefile commands (make check, make test, etc.) NOT raw npx/pnpm/uv
3. Proper API patterns (/api/v1/, auth, pagination)
4. Frontend patterns (@/ imports, TanStack Query hooks)
5. Database rules (ULID, soft deletes, org-scoped)
6. Testing frameworks (pytest, vitest, Playwright)
7. HIPAA compliance (no PHI logging, audit trails)

Respond with the JSON format specified in your instructions.
"""

        response = llm.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
        )

        result = response.content
        if isinstance(result, list):
            result = "".join([str(x) for x in result])
        result = result.strip()

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                json_str = result.split("```")[1].split("```")[0].strip()
            else:
                json_str = result

            review_result = json.loads(json_str)

            status = review_result.get("status", "APPROVED")
            issues_found = review_result.get("issues_found", [])
            corrections = review_result.get("corrections", [])
            revised_description = review_result.get("revised_description")

            if status == "APPROVED":
                print(f"  ✅ {identifier}: Compliant with project rules")
            else:
                print(f"  🔧 {identifier}: Found {len(issues_found)} issue(s)")
                for idx, issue_desc in enumerate(issues_found, 1):
                    print(f"     {idx}. {issue_desc}")

                # Apply corrections if we have a revised description
                if revised_description and corrections:
                    print(f"  📝 Applying {len(corrections)} correction(s)...")
                    for corr in corrections:
                        action = corr.get("action", "FIX")
                        target = corr.get("target", "unknown")
                        reason = corr.get("reason", "")
                        print(f"     [{action}] {target}: {reason}")

                    # Update the issue description in Linear
                    if update_issue_description(issue_id, revised_description):
                        print(f"  ✅ {identifier}: Description updated with fixes")
                        fixed_count += 1
                    else:
                        print(f"  ⚠️  {identifier}: Could not update description")

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"  ⚠️  {identifier}: Could not parse review response: {e}")
            # Fall back to approving if we can't parse
            print("  ➡️  Proceeding with ticket as-is")

        # Move to Human Review
        if update_issue_status(issue_id, "Human: Spec Approve"):
            print(f"  📤 {identifier}: Moved to Human: Spec Approve")
        else:
            print(f"  ⚠️  {identifier}: Could not move to Human: Spec Approve")

        reviewed_count += 1

    print(f"\n🔍 Spec Review Complete: {reviewed_count} reviewed, {fixed_count} fixed")
    return {
        "spec_review_status": "complete",
        "spec_reviewed": reviewed_count,
        "spec_fixed": fixed_count,
    }
