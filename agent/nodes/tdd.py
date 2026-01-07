from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.file_io import write_file, read_project_rules
from config import AGENT_CONFIG
import re

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=AGENT_CONFIG["tdd"]["model"], temperature=AGENT_CONFIG["tdd"]["temperature"]
)

SYSTEM_PROMPT = """You are the TDD Architect (Test Driven Development).
Your goal is to write the automated tests that define the success criteria for the requested feature.
These tests MUST fail initially (red) and pass once the code is correctly implemented (green).

You must output valid test code for:
1. Backend (Pytest) - if the task involves API/Database changes.
2. Frontend (Vitest/React Testing Library) - if the task involves UI changes.

OUTPUT FORMAT:
For each file you want to create, start with a line: `// FILENAME: path/to/file`
Then follow with the code block.

Example:
// FILENAME: apps/backend/tests/test_feature.py
```python
def test_feature():
    ...
```

// FILENAME: apps/frontend/src/components/__tests__/Feature.test.tsx
```tsx
test("renders feature", () => {
    ...
})
```

RULES:
- Backend tests go to: `apps/backend/tests/test_{entity}.py`
- Frontend tests go to: `apps/frontend/src/components/__tests__/{Entity}.test.tsx` (or appropriate path)
- Use `client` fixture for backend integration tests.
- Use mocks where appropriate but prefer integration tests for backend.
- Ensure you import types or client correctly (predict the names based on standard conventions).
- Backend Entity name convention: `test_users.py` implies `User` entity.
- Frontend Component name convention: `UserTable.tsx` implies `UserTable` component.
"""


def tdd_node(state):
    print("🧪 TDD: Writing tests before code...")
    task = state.get("task")
    if not task:
        print("⚠️ TDD: No task found!")
        return {"status": "error"}

    project_rules = read_project_rules()

    prompt = f"""
    Task: {task}

    Project Rules (Context):
    {project_rules}

    INSTRUCTIONS:
    1. Analyze the task to identify the entities and features.
    2. Write the Backend Tests (Pytest) if needed.
    3. Write the Frontend Tests (Vitest) if needed.
    4. ensure filenames follow the monorepo structure (`apps/backend/...`, `apps/frontend/...`).
    5. Output the files using the `// FILENAME:` marker.
    """

    response = llm.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
    )
    content = response.content
    if isinstance(content, list):
        content = "".join([str(x) for x in content])

    # Extract all files
    # Regex to find "// FILENAME: <path>" followed by code blocks
    # We'll split the content by "// FILENAME:"

    parts = re.split(r"// FILENAME:", content)

    # The first part is usually empty or preamble, skip it if it doesn't look like a file definition
    # But strictly, the split will put the path at the start of the chunk.

    created_files = []

    for i, part in enumerate(parts):
        if i == 0:
            continue  # Skip preamble before first filename

        # Part looks like: " apps/backend/tests/foo.py\n```python\ncode...```\n"
        lines = part.strip().split("\n", 1)
        if not lines:
            continue

        filepath = lines[0].strip()
        file_content = lines[1] if len(lines) > 1 else ""

        # Clean up markdown code blocks
        # Remove ```python, ```tsx, ``` at start/end
        # We need to be careful not to remove internal code blocks if any (unlikely in this context)
        # But usually the whole chunk is the code.

        # Simple cleaner: remove the first line if it starts with ``` and the last line if it is ```
        file_lines = file_content.strip().split("\n")

        cleaned_lines = []
        in_code_block = False

        # Iterate to find the main code block
        # Heuristic: The content usually is wrapped in one big ``` block.
        # We'll just strip all lines starting with ``` from the beginning and end.

        # Alternative: Regex replace
        code_clean = re.sub(
            r"^```\w*\s*", "", file_content.strip(), count=1
        )  # Remove first ```lang
        code_clean = re.sub(r"\s*```$", "", code_clean, count=1)  # Remove last ```

        # Also clean up any leading/trailing whitespace
        code_code = code_clean.strip()

        print(f"🧪 TDD: Created test file: {filepath}")
        write_file(filepath, code_code)
        created_files.append(filepath)

    return {"tdd_status": "done", "test_files": created_files}
