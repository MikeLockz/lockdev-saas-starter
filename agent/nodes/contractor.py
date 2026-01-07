from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.file_io import write_file, update_prisma_schema, read_project_rules
from config import AGENT_CONFIG
import re

# Using Gemini for high-reasoning logic
llm = ChatGoogleGenerativeAI(
    model=AGENT_CONFIG["contractor"]["model"],
    temperature=AGENT_CONFIG["contractor"]["temperature"],
)

SYSTEM_PROMPT = """You are the API Contract Architect.
Your goal is to output a perfect TypeScript Definition file AND a Prisma Model.

You must always define:
1. 'DbEntity': The TypeScript interface.
2. 'UiEntity': The formatted TypeScript interface.
3. 'PrismaModel': The model block for schema.prisma.

Output the filename for the TS file in the first line as: `// FILENAME: src/types/your-entity.ts`
Output the Prisma model inside a block starting with `// PRISMA:`.
"""


def contractor_node(state):
    print("🤝 Contractor: Negotiating interface...")
    task = state.get("task")
    if not task:
        print("⚠️ Contractor: No task found!")
        return {"status": "error"}

    project_rules = read_project_rules()

    # 1. Draft & Critique (Middle-Out Strategy)
    prompt = f"""
    Task: {task}

    Project Rules (Context):
    {project_rules}
    
    Step 1: Analyzye the Domain.
    Step 2: Draft the TypeScript interfaces (DbEntity, UiEntity).
    Step 3: Draft the Prisma Model (model Name {{ ... }}).
    Step 4: Critique and Refactor.
    Step 5: Final Output.
    - START the response with the filename comment: `// FILENAME: src/types/lower-case-entity.ts`
    - Include the TypeScript interfaces.
    - Include the Prisma model block starting with `// PRISMA:`.
    """

    response = llm.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
    )
    content = response.content
    if isinstance(content, list):
        content = "".join([str(x) for x in content])
    content = content.strip()

    # Extract Prisma Model
    prisma_match = re.search(
        r"// PRISMA:\s*(model .+?\s*\{.+?\})", content, re.DOTALL | re.MULTILINE
    )
    if prisma_match:
        prisma_model = prisma_match.group(1).strip()
        print("💾 Contractor: Updating Prisma Schema...")
        update_prisma_schema(prisma_model)

    # Extract Filename
    filename_match = re.search(r"^// FILENAME: (.+)", content, re.MULTILINE)
    if filename_match:
        contract_path = filename_match.group(1).strip()
    else:
        contract_path = "src/types/contract.ts"

    # Clean up Markdown for TS file
    clean_content = content
    # Remove the PRISMA block from the TS file content if it's there
    clean_content = re.sub(r"// PRISMA:.*", "", clean_content, flags=re.DOTALL).strip()
    clean_content = (
        clean_content.replace("```typescript", "").replace("```", "").strip()
    )

    # Save the Contract
    print(f"📝 Contractor: Writing contract to {contract_path}")
    write_file(contract_path, clean_content)

    return {"contract_path": contract_path, "status": "contract_locked"}
