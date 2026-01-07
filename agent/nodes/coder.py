# agent/nodes/coder.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.file_io import write_file, read_file, read_project_rules
from config import AGENT_CONFIG
import os

llm = ChatGoogleGenerativeAI(
    model=AGENT_CONFIG["coder"]["model"],
    temperature=AGENT_CONFIG["coder"]["temperature"],
)


def coder_node(state):
    mode = state.get("coder_mode", "general")  # 'backend' or 'frontend'
    contract_path = state.get("contract_path")
    contract_content = read_file(contract_path)
    error = state.get("error")  # Capture any error from Reviewer
    project_rules = read_project_rules()

    # Infer entity name from filename (e.g. 'src/types/user.ts' -> 'user')
    entity_name = os.path.splitext(os.path.basename(contract_path))[0]

    # Determine output path
    if mode == "backend":
        output_path = f"src/app/api/{entity_name}/route.ts"
    elif mode == "frontend":
        output_path = f"src/components/{entity_name.capitalize()}Table.tsx"

    print(f"👷 Coder ({mode.upper()}): Working on '{entity_name}'...")

    # --- BASE PROMPTS ---
    if mode == "backend":
        system_prompt = "You are a Backend Engineer. Output ONLY valid TypeScript code for a Next.js API route. Do NOT output Prisma Schema."
        user_prompt = f"""
        Read the Contract:
        {contract_content}
        
        Project Rules (Context):
        {project_rules}
        
        Task: Implement the Next.js API route (e.g. GET /api/{entity_name}) that returns 'UiEntity'.
        
        CRITICAL IMPORT RULES:
        1. Use `import {{ prisma }} from '@/lib/prisma'` for database access.
        2. Use `import {{ Db..., Ui... }} from '@/types/{entity_name}'` for types.
        3. Do NOT use relative paths like `../../../`.
        
        OUTPUT ONLY THE TYPESCRIPT CODE.
        """

    elif mode == "frontend":
        system_prompt = "You are a Frontend Engineer. Output ONLY valid TypeScript/React code. No conversation."
        user_prompt = f"""
        Read the Contract:
        {contract_content}
        
        Project Rules (Context):
        {project_rules}
        
        Task: Build the UI Component for '{entity_name}'.
        1. It must accept 'UiEntity' properties.
        2. It must fetch from '/api/{entity_name}'.
        
        CRITICAL IMPORT RULES:
        1. Use `import {{ Ui... }} from '@/types/{entity_name}'` for types.
        2. Do NOT use relative paths like `../types`.
        
        OUTPUT ONLY THE CODE.
        """

    # --- REPAIR MODE ---
    if error:
        print(f"🛠️ Coder: Fixing {mode} error...")
        current_code = read_file(output_path)
        user_prompt = f"""
        FIX THIS CODE. Output ONLY the corrected full file content. No conversation.
        
        Current Code:
        {current_code}
        
        Error Report from Linter/Tests:
        {error}
        
        Project Rules (Context):
        {project_rules}
        
        INSTRUCTION: Fix the code to resolve the error. Ensure it still satisfies the contract.
        """

    response = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    )

    # Clean up Markdown
    content = response.content
    if isinstance(content, list):
        content = "".join([str(x) for x in content])
    content = (
        content.replace("```typescript", "")
        .replace("```tsx", "")
        .replace("```", "")
        .strip()
    )

    print(f"👷 Coder: Writing {mode} implementation to {output_path}")
    write_file(output_path, content)

    # Clear error after fixing attempt
    return {f"{mode}_status": "done", "error": None}
