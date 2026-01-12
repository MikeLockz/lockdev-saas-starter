import os

# Default to the working model found previously
DEFAULT_MODEL = "gemini-3-flash-preview"
REASONING_MODEL = "gemini-3-pro-preview"

AGENT_CONFIG = {
    "pm": {
        "model": os.getenv("PM_MODEL", REASONING_MODEL),
        "temperature": 0.7,  # Slightly creative for user stories
    },
    "contractor": {
        "model": os.getenv("CONTRACTOR_MODEL", REASONING_MODEL),
        "temperature": 0,
    },
    "coder": {"model": os.getenv("CODER_MODEL", DEFAULT_MODEL), "temperature": 0},
    "reviewer": {"model": os.getenv("REVIEWER_MODEL", DEFAULT_MODEL), "temperature": 0},
    "staff_engineer": {
        "model": os.getenv("STAFF_ENGINEER_MODEL", REASONING_MODEL),
        "temperature": 0.3,  # Balanced for structured output
    },
    "spec_reviewer": {
        "model": os.getenv("SPEC_REVIEWER_MODEL", REASONING_MODEL),
        "temperature": 0.2,  # More deterministic for review
    },
    "tdd": {
        "model": os.getenv("TDD_MODEL", REASONING_MODEL),
        "temperature": 0.1,  # Deterministic for tests
    },
}
