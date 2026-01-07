import os

# Security: Allow writing to the project root (apps/ etc)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
AGENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def write_file(relative_path, content):
    """Writes content to a file in the project."""
    if ".." in relative_path or relative_path.startswith("/"):
        return "Error: Invalid path. Must be relative to project root."

    full_path = os.path.join(BASE_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w") as f:
        f.write(content)

    return f"Successfully wrote to {relative_path}"


def read_file(relative_path):
    """Reads content from a file in the project."""
    if ".." in relative_path or relative_path.startswith("/"):
        return "Error: Invalid path. Must be relative to project root."

    full_path = os.path.join(BASE_DIR, relative_path)

    if not os.path.exists(full_path):
        return f"Error: File {relative_path} not found."

    with open(full_path, "r") as f:
        return f.read()


def read_project_rules():
    """Reads the compiled project rules from agent/config/project_rules.md."""
    rules_path = os.path.join(AGENT_DIR, "config/project_rules.md")
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def update_prisma_schema(model_content):
    """Appends or replaces a model in schema.prisma."""
    schema_path = os.path.join(BASE_DIR, "prisma/schema.prisma")
    os.makedirs(os.path.dirname(schema_path), exist_ok=True)

    # Simple strategy: append for now.
    # A better one would check if 'model User' exists and replace it.
    with open(schema_path, "a") as f:
        f.write("\n" + model_content + "\n")

    return "Updated prisma/schema.prisma"
