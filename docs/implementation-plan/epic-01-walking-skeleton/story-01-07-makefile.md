# Story 1.7: The Makefile
**User Story:** As a Developer, I want standard commands for common tasks, so that I don't have to remember complex CLI arguments.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 1.7 from `docs/03`

## Technical Specification
**Goal:** Create a root `Makefile`.

**Changes Required:**
1.  **File:** `Makefile`
    - `install-all`: Backend sync + Frontend install.
    - `dev`: Run backend (honcho/uvicorn) locally.
    - `migrate`: Run Alembic.
    - `check`: Run lint/test/typecheck.
    - `test`: Run pytest + vitest.

## Acceptance Criteria
- [ ] `make install-all` works.
- [ ] `make check` runs all linters.

## Verification Plan
**Manual Verification:**
- Run `make install-all` and `make check`.
