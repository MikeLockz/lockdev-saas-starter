# Global Instructions
**Usage:** This file applies to EVERY agent interaction.

## 1. Context Awareness
- **Always** read `docs/03 - implementation.md` before starting a task to understand the "Big Picture".
- **Always** check `docs/05 - API Reference.md` when working on backend endpoints or frontend API clients.
- **Always** check `docs/06 - Frontend Views & Routes.md` and `docs/07 - front end components.md` when building UI.
- **Always** check the "Traceability Matrix" in the current Epic's `index.md` to see where you are.

## 2. Code Style & Standards
- **Strictly Adhere** to the project's tooling:
    - **Backend:** Python 3.11+, `uv`, `ruff` (lint/format), `mypy` (types).
    - **Frontend:** React, TypeScript, `pnpm`, `biome` (lint/format), `vitest`.
    - **Infra:** OpenTofu, Docker Compose, `make`.
- **Do NOT** use Prettier (use Biome).
- **Do NOT** use Poetry/Pipenv (use `uv`).

## 3. Safety & Security
- **HIPAA Compliance:**
    - Never hardcode PII/PHI in tests or logs.
    - Always verify RLS policies when touching DB.
    - Ensure Audit Logs are triggered for sensitive actions.
- **Secrets:**
    - Never commit `.env`.
    - Use `sops` patterns for secret management.

## 4. Development Environment
-   **Startup:** Always run `make dev` or `docker compose up` in detached mode (background) to avoid blocking the terminal. Use `make dev` (modify Makefile if needed) or `docker compose up -d`).
-   **Logs:** When running in detached mode, verify startup by tailing logs: `docker compose logs -f api` or `docker compose logs -f web`).
-   **Ports:**
    -   Frontend: `http://localhost:5173`
    -   Backend: `http://localhost:8000`
    -   Mailpit: `http://localhost:8025` (if enabled)


## 5. Command Execution & Safety
- **Environment:**
    - **ALWAYS** set `CI=true` for shell commands to disable interactive prompts and UI popups.
- **Testing Tools:**
    - **Playwright:**
        - Always append `--reporter=list` or `--reporter=line` for readable terminal output.
        - **NEVER** run in "headed" mode; always use `--headless`.
- **Mandatory Timeouts:**
    - **NEVER** run blocking commands (e.g., `npm install`, `docker compose up`, `alembic upgrade`) without a timeout.
    - Use `timeout <seconds>` or tool-specific flags (e.g., `wait-for-it`, `--max-time`).
    - Standard timeout: **300s** (5 minutes) for installs/builds, **60s** for checking status.
    - **Hanging Commands:** If a command is likely to hang (like a dev server), use a timeout OR run it in the background with a health check.
- **Monitoring:**
    - **ALWAYS** check exit codes (`echo $?`) immediately after execution.
    - **Stream Output:** For long processes, ensure output is visible or logged to a file that can be read if it hangs.
- **Cleanliness:**
    - If a command times out or fails, **immediately** clean up partial state (e.g., delete partial node_modules, stop stuck containers).
    - **Zombie Processes:** Be aware of background processes. Use `pkill` or `docker kill` if a tool does not exit cleanly.
