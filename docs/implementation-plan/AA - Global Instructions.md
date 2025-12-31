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

## 4. Work Process
1.  **Read** the Story file completely.
2.  **Verify** prerequisites (previous stories).
3.  **Implement** changes (Red-Green-Refactor).
4.  **Verify** using the defined "Verification Plan" in the story.
5.  **Update** the Epic's `index.md` to mark the story as `[x]`.
