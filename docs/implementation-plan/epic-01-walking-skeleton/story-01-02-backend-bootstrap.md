# Story 1.2: Backend Bootstrap (FastAPI + UV)
**User Story:** As a Backend Developer, I want a Python project initialized with `uv` and FastAPI, so that I have a modern, fast environment.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 1.2 from `docs/03`

## Technical Specification
**Goal:** Initialize `backend/` with `pyproject.toml` and dependencies.

**Changes Required:**
1.  **File:** `backend/pyproject.toml`
    - Create using `uv`.
    - Dependencies: `fastapi`, `uvicorn[standard]`, `structlog`, `presidio-analyzer`, `google-cloud-aiplatform`, `arq`, `asyncpg`, `python-ulid`, `slowapi`, `httpx`, `sentry-sdk[fastapi]`, `secure`, `honcho`, `stripe`.
    - Python version: `>=3.11`.

## Acceptance Criteria
- [ ] `uv sync` runs successfully in `backend/`.
- [ ] `fastapi` and dependencies are installed in the virtual environment.

## Verification Plan
**Manual Verification:**
- Command: `cd backend && uv sync && uv run python -c "import fastapi; print(fastapi.__version__)"`
- Expected Output: Prints FastAPI version (e.g., `0.109.0`).
