# Story 2.3: Migrations (Alembic)
**User Story:** As a Developer, I want version-controlled database migrations, so that schema changes are safe and reproducible.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 2.3 from `docs/03`

## Technical Specification
**Goal:** Initialize Alembic.

**Changes Required:**
1.  **File:** `backend/alembic.ini`
2.  **File:** `backend/migrations/env.py`
    - Configure to use `src.config.settings.DATABASE_URL`.
    - Configure to use Async engine.
    - Import `Base` metadata from models.

## Acceptance Criteria
- [ ] `alembic revision --autogenerate` works.
- [ ] `alembic upgrade head` works.

## Verification Plan
**Manual Verification:**
- Run `make migrate`.
