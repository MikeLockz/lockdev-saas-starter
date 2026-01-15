# Story 1.4: Frontend Bootstrap (Vite + React)
**User Story:** As a Frontend Developer, I want a Vite project with React and TypeScript, so that I can begin UI development.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.4 from `docs/03`

## Technical Specification
**Goal:** Initialize `frontend/` with Vite, React, TS, and Axios security.

**Changes Required:**
1.  **Initialization:** `pnpm create vite . --template react-ts` inside `frontend/`.
2.  **Dependencies:**
    - `zustand`
    - `@tanstack/react-query`
    - `@tanstack/react-router`
    - `axios`
3.  **File:** `frontend/src/lib/axios.ts`
    - Configure global Axios instance.
    - **Security:** Implement domain whitelisting interceptor (Block requests to non-whitelisted domains).

## Acceptance Criteria
- [ ] Frontend builds and runs locally.
- [ ] Axios interceptor blocks requests to `evil.com`.

## Verification Plan
**Manual Verification:**
- Command: `cd frontend && pnpm dev`
- Action: Visit `http://localhost:5173`.
- Test: In browser console, try using the axios instance to fetch `https://google.com` (should be blocked if not whitelisted).
