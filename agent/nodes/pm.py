from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.file_io import read_project_rules
from tools.linear_adapter import (
    fetch_issues,
    update_issue_description,
    update_issue_status,
)
from config import AGENT_CONFIG
from typing import Dict, Any

# Using Gemini for PM reasoning
llm = ChatGoogleGenerativeAI(
    model=AGENT_CONFIG.get("pm", {}).get("model", "gemini-2.0-flash"),
    temperature=AGENT_CONFIG.get("pm", {}).get("temperature", 0.7),
)

SYSTEM_PROMPT = """You are a Senior Product Manager with deep expertise in writing clear, actionable user stories.

Your job is to take a bare ticket title/description and transform it into a comprehensive product specification. Focus on the "WHAT" (requirements), not the "HOW" (technical implementation).

If attachments (images, mockups, designs) are provided, analyze them and incorporate specific visual/UX requirements into your user story.

## IMPORTANT RULES:
- Do NOT include technical implementation details (no code, no frameworks, no architecture)
- Do NOT suggest HOW to build it - only WHAT to build
- Do NOT repeat the user story in a separate description section
- DO include specific views/routes where the feature will be available
- DO write complete, narrative user stories with full context

Always output in this exact format:

## User Story
[Write a complete, narrative user story that explains WHO needs this feature, WHAT they need to accomplish, WHY it matters to them, and the specific BEHAVIOR expected. This should be detailed enough that someone can understand the full scope without additional context. Include edge cases and error states.]

## Acceptance Criteria
- [ ] Feature is accessible from [specific view/route, e.g., /dashboard, /patients/:id]
- [ ] [Specific, testable user-facing criterion]
- [ ] [Specific, testable user-facing criterion]
- [ ] [Error handling: what happens when X fails]
- [ ] [Add more as needed]

## UI/UX Requirements
[Describe the expected visual appearance, interactions, and user flow. Reference any attached mockups.]

## Referenced Attachments
[List any attachments analyzed with notes on what they show - or "None" if no attachments]

## Out of Scope
- [What is explicitly NOT included in this ticket]

Be specific, actionable, and user-focused. Every criterion should describe WHAT the user experiences, not how it's built.
"""


def format_attachments(attachments_data: dict) -> str:
    """Format attachments for inclusion in the prompt."""
    nodes = attachments_data.get("nodes", [])
    if not nodes:
        return "(No attachments)"

    formatted = []
    for i, att in enumerate(nodes, 1):
        title = att.get("title") or "Untitled"
        subtitle = att.get("subtitle") or ""
        url = att.get("url") or ""
        source_type = att.get("sourceType") or "unknown"

        attachment_info = f"{i}. **{title}**"
        if subtitle:
            attachment_info += f" - {subtitle}"
        attachment_info += f"\n   Type: {source_type}"
        if url:
            attachment_info += f"\n   URL: {url}"

        formatted.append(attachment_info)

    return "\n".join(formatted)


def pm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Product Manager agent that:
    1. Polls Linear for 'Backlog' tickets
    2. Analyzes any attachments/images on the ticket
    3. Fleshes out user stories with acceptance criteria
    4. Updates the ticket description
    5. Moves ticket to 'Spec Review' for human approval
    """
    print("📋 PM Agent: Looking for Backlog tickets to refine...")

    issues = fetch_issues("AI: Product Backlog")

    if not issues:
        print("💤 PM Agent: No Backlog (AI: Product Backlog) tickets found. Resting.")
        return {"pm_status": "idle", "pm_processed": 0}

    project_rules = read_project_rules()
    processed_count = 0

    for issue in issues:
        issue_id = issue["id"]
        identifier = issue["identifier"]
        title = issue["title"]
        existing_description = issue.get("description") or ""
        attachments = issue.get("attachments", {})

        # Skip if already has a fleshed-out description (contains "## Acceptance Criteria")
        if "## Acceptance Criteria" in existing_description:
            print(f"⏭️  PM Agent: {identifier} already has user story. Skipping.")
            continue

        # Format attachments for the prompt
        attachments_text = format_attachments(attachments)
        attachment_count = len(attachments.get("nodes", []))

        if attachment_count > 0:
            print(
                f"✍️  PM Agent: Writing user story for {identifier}: {title} (📎 {attachment_count} attachments)"
            )
        else:
            print(f"✍️  PM Agent: Writing user story for {identifier}: {title}")

        prompt = f"""
Ticket Title: {title}

Existing Description (if any):
{existing_description if existing_description else "(No description provided)"}

Attachments:
{attachments_text}

Project Context:
{project_rules}

Please write a comprehensive user story for this ticket. If there are attachments (especially images or mockups), analyze them and incorporate specific visual/UI requirements into your acceptance criteria.
"""

        response = llm.invoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
        )

        # Clean up response content
        new_description = response.content
        if isinstance(new_description, list):
            new_description = "".join([str(x) for x in new_description])
        new_description = new_description.strip()

        # Update the ticket description
        success = update_issue_description(issue_id, new_description)
        if success:
            print(f"✅ PM Agent: Updated {identifier} with user story")

            status_success = update_issue_status(issue_id, "Human: Product Approve")
            if status_success:
                print(f"📤 PM Agent: Moved {identifier} to Human: Product Approve")
            else:
                print(
                    f"⚠️  PM Agent: Could not move {identifier} to Human: Product Approve"
                )

            processed_count += 1
        else:
            print(f"❌ PM Agent: Failed to update {identifier}")

    print(f"📋 PM Agent: Processed {processed_count} tickets")
    return {"pm_status": "complete", "pm_processed": processed_count}
