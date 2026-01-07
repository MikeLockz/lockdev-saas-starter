import json
import os
import sys

# Add backend directory to path so we can import src
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.main import app


def generate_schema():
    openapi_schema = app.openapi()
    print(json.dumps(openapi_schema, indent=2))


if __name__ == "__main__":
    generate_schema()
