# Story 3.1: Shadcn UI Setup
**User Story:** As a Designer, I want a consistent UI component library, so that the app looks professional and accessible.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.1 from `docs/03`
- **Docs Ref:** `docs/07 - front end components.md`

## Technical Specification
**Goal:** Initialize shadcn-ui and install core components.

**Changes Required:**
1.  **Config:** `components.json`.
2.  **Dependencies:** `zod`, `react-hook-form`, `@hookform/resolvers`.
3.  **Components:** Install `button`, `input`, `form`, `card`, `dialog`, `dropdown-menu`, `toast`, `avatar`, `skeleton`.

## Acceptance Criteria
- [x] `npx shadcn-ui@latest add button` works.
- [x] Components render correctly in a test page.

## Verification Plan
**Manual Verification:**
- Add a Button to `App.tsx` and verify styling.
