import json
import os

from fastapi.openapi.utils import get_openapi

from src.main import app  # <--- Import your actual FastAPI app

# Configuration
# Resolve to the /contracts directory at the repository root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
OUTPUT_DIR = os.path.join(REPO_ROOT, "contracts")


def get_referenced_schemas(schema, all_schemas, collected=None):
    """
    Recursively find all schemas referenced by a specific schema.
    If Ticket refs User, we must collect User too.
    """
    if collected is None:
        collected = set()

    # Base case: precise reference
    if "$ref" in schema:
        ref_name = schema["ref"].split("/")[-1] if "ref" in schema else schema["$ref"].split("/")[-1]
        if ref_name not in collected:
            collected.add(ref_name)
            # Recursively check the child schema for more refs
            if ref_name in all_schemas:
                get_referenced_schemas(all_schemas[ref_name], all_schemas, collected)
        return collected

    # Recursive search for $ref keys in nested dicts/lists
    if isinstance(schema, dict):
        for value in schema.values():
            get_referenced_schemas(value, all_schemas, collected)
    elif isinstance(schema, list):
        for item in schema:
            get_referenced_schemas(item, all_schemas, collected)

    return collected


def generate_contracts():
    print("⏳ Generating Monolith...")
    openapi = get_openapi(title="Backtest", version="1.0", routes=app.routes)

    all_schemas = openapi.get("components", {}).get("schemas", {})
    paths = openapi.get("paths", {})

    # Bucket to hold { "Ticket": {"Ticket", "User", "Address"} }
    tag_to_models = {}

    print("🔍 Analyzing Routes & Tags...")
    for _path, methods in paths.items():
        for _method, op in methods.items():
            tags = op.get("tags", ["Common"])

            # Find root models used in this endpoint
            endpoint_root_models = set()

            # Check Request Body
            if "requestBody" in op:
                try:
                    schema = op["requestBody"]["content"]["application/json"]["schema"]
                    get_referenced_schemas(schema, all_schemas, endpoint_root_models)
                except (KeyError, TypeError):
                    pass

            # Check Responses
            for _code, resp in op.get("responses", {}).items():
                try:
                    schema = resp["content"]["application/json"]["schema"]
                    get_referenced_schemas(schema, all_schemas, endpoint_root_models)
                except (KeyError, TypeError):
                    pass

            # Assign found models (and their recursive children) to the Tag
            for tag in tags:
                if tag not in tag_to_models:
                    tag_to_models[tag] = set()
                tag_to_models[tag].update(endpoint_root_models)

    # Output Files
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"💾 Writing Contracts to /{OUTPUT_DIR}...")
    for tag, model_names in tag_to_models.items():
        # Build the schema subset
        subset_definitions = {}
        for name in model_names:
            if name in all_schemas:
                subset_definitions[name] = all_schemas[name]

        contract = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": f"{tag} Domain Contract",
            "description": f"Auto-generated contract for {tag} feature",
            "definitions": subset_definitions,
        }

        filename = f"{OUTPUT_DIR}/{tag.lower()}.json"
        with open(filename, "w") as f:
            json.dump(contract, f, indent=2)
            print(f"   - {filename} ({len(model_names)} models)")


if __name__ == "__main__":
    generate_contracts()
