# Story 3.2: API Type Generation
**User Story:** As a Developer, I want end-to-end type safety, so that I catch API integration errors at compile time.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.2 from `docs/03`

## Technical Specification
**Goal:** Auto-generate TS types and Zod schemas from FastAPI OpenAPI.

**Changes Required:**
1.  **File:** `backend/scripts/generate_schema.py`
    - Dumps `openapi.json` without DB connection.
2.  **Frontend:**
    - Install `openapi-typescript` and `openapi-zod-client`.
    - Script `generate:types` in `package.json`.

## Acceptance Criteria
- [x] `pnpm generate:types` creates `src/lib/api-types.d.ts`.
- [x] `pnpm generate:types` creates `src/lib/api-schemas.ts`.

## Verification Plan
**Manual Verification:**
- Run script. Check generated files exist and contain User model.
