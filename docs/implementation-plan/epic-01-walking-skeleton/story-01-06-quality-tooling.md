# Story 1.6: Quality Tooling & Enforcement
**User Story:** As a Developer, I want automated linting and formatting, so that the codebase remains consistent and clean.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 1.6 from `docs/03`

## Technical Specification
**Goal:** Configure `biome`, `ruff`, and `pre-commit`.

**Changes Required:**
1.  **File:** `biome.json` (Root) - Config for TS/JS/JSON.
2.  **File:** `.pre-commit-config.yaml`
    - Hooks: `ruff`, `ruff-format`, `biome-check`.
3.  **Backend Config:** Add `[tool.ruff]` to `pyproject.toml`.

## Acceptance Criteria
- [ ] `pre-commit run --all-files` passes.
- [ ] Biome formats frontend code.
- [ ] Ruff formats backend code.

## Verification Plan
**Manual Verification:**
- Command: `pnpm biome check .`
- Command: `uv run ruff check .`
