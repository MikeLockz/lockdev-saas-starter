from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.git import checkout, commit, push, create_pr, run_git_command
from tools.linear_adapter import fetch_parent_issue, fetch_sub_issues
from config import AGENT_CONFIG

# Initialize LLM for risk assessment
llm = ChatGoogleGenerativeAI(
    model=AGENT_CONFIG["publisher"]["model"]
    if "publisher" in AGENT_CONFIG
    else AGENT_CONFIG["pm"]["model"],
    temperature=0.3,
)

RISK_SYSTEM_PROMPT = """You are a Release Manager and Risk Assessor.
Your goal is to analyze the changes made in a Pull Request (via git stats or file names) and identify the Top 3 Riskiest Changes.

Risk Factors include:
- Database schema changes (schema.prisma, migrations)
- Core data models (src/types)
- Authentication/Authorization (security, permissions, policies)
- New API Routes (src/app/api)
- Large UI additions (src/components/...)
- Infrastructure changes (Dockerfile, terraform, etc.)

Output Format:
Return a Markdown list of the Top 3 risks. For each, explain WHY it is risky.

Example:
1. **Database Schema Change**: Modified `User` table in `schema.prisma`. Requires migration.
2. **New API Endpoint**: Added `POST /api/billing`. Needs security review.
3. **Auth Logic**: Changed `middleware.ts`. High regression risk.
"""


def publisher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles Git operations:
    1. Git checkout/switch to feature branch (feature/{parent-id})
    2. Git add . && git commit -m "feat({id}): {title}"
    3. Git push
    4. Check if ALL sub-issues are done
    5. If ALL done -> Create PR with Risk Assessment
    """
    print("📦 Publisher: Managing Version Control...")

    issue_id = state.get("ticket_id")
    if not issue_id:
        print("⚠️ Publisher: No ticket ID found. Skipping.")
        return {"publisher_status": "skipped"}

    # 1. Fetch info
    parent = fetch_parent_issue(issue_id)
    if not parent:
        print("⚠️ Publisher: Could not find parent ticket. Is this a sub-issue?")
        # Fallback: Treat as standalone if no parent? Probaly not for now.
        return {"publisher_status": "skipped"}

    parent_identifier = parent["identifier"]
    branch_name = f"feature/{parent_identifier.lower()}"

    # 2. Checkout Branch
    success, output = checkout(branch_name, create_if_missing=True)
    if not success:
        print(f"❌ Publisher: Failed to checkout {branch_name}: {output}")
        return {"publisher_status": "failed", "error": output}

    print(f"🌿 Publisher: On branch {branch_name}")

    # 3. Commit
    sub_issues = fetch_sub_issues(parent["id"])
    current_issue = next((i for i in sub_issues if i["id"] == issue_id), None)

    if current_issue:
        commit_msg = f"feat({current_issue['identifier']}): {current_issue['title']}"
    else:
        commit_msg = f"feat({issue_id}): Implement sub-task"

    success, output = commit(commit_msg)
    if success:
        print(f"💾 Publisher: Committed changes - {commit_msg}")
    elif "clean" in output:
        print("⚠️ Publisher: Nothing to commit (clean working tree).")
    else:
        print(f"❌ Publisher: Commit failed: {output}")

    # 4. Push
    success, output = push(branch_name)
    if success:
        print("⬆️  Publisher: Pushed branch to origin")
    else:
        print(f"❌ Publisher: Push failed: {output}")

    # 5. Check if we should open PR
    completed_statuses = ["Human: Final Approval", "Done", "Canceled"]
    pending_issues = [
        i for i in sub_issues if i["state"]["name"] not in completed_statuses
    ]

    if not pending_issues:
        print("🎉 Publisher: All sub-issues complete! Preparing PR...")

        # --- RISK ANALYSIS ---
        print("🕵️ Publisher: Analyzing risks...")
        # Get diff stats against main
        success, diff_stats = run_git_command(
            ["git", "diff", "--stat", "origin/main...HEAD"]
        )
        if not success:
            # Fallback to local main if origin not available or fetch needed
            success, diff_stats = run_git_command(
                ["git", "diff", "--stat", "main...HEAD"]
            )

        if success:
            risk_prompt = f"""
            Analyze these file changes and identify the Top 3 Riskiest things:
            
            {diff_stats}
            
            Parent Ticket: {parent["title"]}
            """
            response = llm.invoke(
                [
                    SystemMessage(content=RISK_SYSTEM_PROMPT),
                    HumanMessage(content=risk_prompt),
                ]
            )
            risk_assessment = response.content
        else:
            risk_assessment = "Could not generate risk assessment (diff failed)."

        # --- PR BODY ---
        pr_title = f"feat({parent_identifier}): {parent['title']}"
        pr_body = f"Implementation for {parent_identifier}\n\n"

        pr_body += "## ⚠️ Risk Assessment\n"
        pr_body += risk_assessment + "\n\n"

        pr_body += "## Sub-tasks\n"
        for sub in sub_issues:
            status = sub["state"]["name"]
            check = "x" if status in completed_statuses else " "
            pr_body += f"- [{check}] {sub['identifier']}: {sub['title']} ({status})\n"

        success, output = create_pr(pr_title, pr_body)
        if success:
            print(f"🚀 Publisher: PR Created: {output}")
        else:
            print(f"⚠️ Publisher: PR Creation failed (or exists): {output}")
    else:
        print(f"⏳ Publisher: {len(pending_issues)} sub-issues remaining. Skipping PR.")
        for p in pending_issues:
            print(f"   - {p['identifier']} ({p['state']['name']})")

    return {"publisher_status": "success"}
