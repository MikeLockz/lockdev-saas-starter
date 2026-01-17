import json
import os
import sys

# Add the backend directory to sys.path to allow importing app
sys.path.append(os.getcwd())

from app.main import app


def generate_schema():
    openapi_schema = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("OpenAPI schema generated to openapi.json")


if __name__ == "__main__":
    generate_schema()
