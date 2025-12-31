# Role
You are an expert Technical Project Manager and Systems Architect. Your objective is to synthesize a single, rigorous, and executable **Detailed Implementation Plan** for an LLM-driven software engineering agent.

# Context
You have access to the following project documentation:
1.  **High-Level Roadmap:** `docs/03 - implementation.md` (The **Master Plan** & backbone/chronology).
2.  **API Specifications:** `docs/05 - API Reference.md` (Detailed endpoints, request/response shapes, error codes).
3.  **Frontend Requirements:** `docs/06 - Frontend Views & Routes.md` (Routes, auth rules, page content).
4.  **Component Architecture:** `docs/07 - front end components.md` (UI component hierarchy and composition).
5.  **State Management:** `docs/08 - front end state management.md` (Store logic, hooks, data layer).

# Conflict Resolution & Precedence
1.  **Docs/03 is Law:** If `docs/03` conflicts with any other document regarding *Technology Choices* or *High-Level Architecture* (e.g., Router choice, Build tools), `docs/03` takes precedence.
    *   *Example:* `docs/08` might use generic React Router examples, but `docs/03` specifies **TanStack Router**. You must use **TanStack Router**.
2.  **Docs/05 is Truth for API:** If `docs/03` lists an endpoint vaguely, `docs/05` defines its exact shape.

# Task
Generate a modular implementation plan in the directory `docs/implementation-plan/`.

**Structure:**
1.  **Global Instructions (`AA` Pattern):** Create `AA - Global Instructions.md` at the root of `docs/implementation-plan/`.
2.  **Master Orchestrator (`00` Pattern):** Create `00 - Master Orchestrator.md` at the root.
3.  **Epic Directories (`epic-NN` Pattern):** Create one **directory** per Phase (Epic) defined in `docs/03` (e.g., `epic-01-walking-skeleton/`).
4.  **Epic Index (`index.md`):** Inside each Epic directory, create an `index.md` file that acts as the Epic's "Read Me" and orchestrator.
5.  **Story Files (`story-NN-MM` Pattern):** Inside each Epic directory, create **separate files** for each Story (Ticket) (e.g., `story-01-01-init-repo.md`).

**Content Expansion:** For each step in `docs/03`, expand it significantly into detailed Stories using the specific details from `docs/05`, `06`, `07`, and `08`.

# Traceability & Accounting
To ensure 100% coverage of the Roadmap (`docs/03`):
1.  **No Omissions:** Every single Step (e.g., Step 1.1) from `docs/03` must be represented as at least one Story file.
2.  **Mapping Table:** The Epic's `index.md` must contain a "Traceability Matrix" table mapping `docs/03` Step IDs to the detailed Story filenames.

# Constraints & Philosophy
... [existing constraints]

# File Output Formats

## 1. Global Instructions (`docs/implementation-plan/AA - Global Instructions.md`)
```markdown
# Global Instructions
**Usage:** This file applies to EVERY agent interaction.
... [Same content as before]
```

## 2. Master Orchestrator (`docs/implementation-plan/00 - Master Orchestrator.md`)
```markdown
# Master Orchestrator
**Objective:** Coordinate the execution of the Lockdev SaaS implementation.

## Progress Log
| Epic | Status | Owner | Directory |
| :--- | :--- | :--- | :--- |
| **Epic 1** | [ ] Pending | Builder | `epic-01-walking-skeleton/` |
...
```

## 3. Epic Index (`docs/implementation-plan/epic-[N]-[Name]/index.md`)
```markdown
# Epic [N]: [Epic Name]
**User Story:** As a [Role], I want [Feature] so that [Business Value].

**Goal:** [One sentence goal summarizing the epic's technical outcome]

## Traceability Matrix
| Roadmap Step (docs/03) | Story File | Status |
| :--- | :--- | :--- |
| Step N.1 | `story-N-01-[name].md` | Pending |

## Execution Order
1.  [ ] `story-N-01-[name].md`
2.  [ ] `story-N-02-[name].md`
...

## Epic Verification
**Completion Criteria:**
- [ ] All stories marked as completed.
- [ ] `pnpm playwright` passes for the epic's scope.
```

## 4. Story File (`docs/implementation-plan/epic-[N]-[Name]/story-[N]-[M]-[Name].md`)
```markdown
# Story [N.M]: [Story Name]
**User Story:** As a [Role], I want to [Action] so that [Outcome].

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step [N.1] from `docs/03`
- **Source:** [Reference to docs/05, 06, etc.]

## Technical Specification
**Goal:** [Specific technical goal of this story]

**Changes Required:**
1.  **File:** `src/path/to/file.ts`
    - Description of change.
2.  **Database:**
    - Schema changes (if any).

## Acceptance Criteria
- [ ] Criterion 1 (e.g., Endpoint returns 201 Created)
- [ ] Criterion 2 (e.g., Data is persisted to Postgres)

## Verification Plan
**Automated Tests:**
- Unit Test Command: `pnpm vitest ...`
- E2E Test Command: `pnpm playwright ...`

**Manual Verification:**
- Command: `curl -X POST ...`
- Expected Output: JSON `{ "id": "..." }`
```

# Key Focus Areas to Expand
1.  **Auth & Security:** Detailed steps for Firebase Admin, User Models, RLS, and Impersonation.
2.  **Frontend Plumbing:** Axios Interceptors, Auth Store, TanStack Query integration.
3.  **Domain Logic:** Complex multi-file implementations for Proxy relationships and Consent tracking.

# Final Validation & Iteration
**Mandatory Self-Correction Loop:**
Before finalizing the plan, you must perform a rigorous audit of your generated files against the input requirements (`docs/03`, `05`, `06`, `07`, `08`).

1.  **Audit:** Compare every single generated Story against the source documents.
    *   *Check:* Did I include all fields from `docs/05` in the API story?
    *   *Check:* Did I include all UI components from `docs/07` in the Frontend story?
    *   *Check:* Did I miss any edge cases from `docs/08`?
2.  **Report:** If you find gaps, list them.
3.  **Fix:** Update the Story files to include the missing details.
4.  **Repeat:** Loop until your internal audit returns **ZERO** missing requirements.

**Generate the files in `docs/implementation-plan/` now, ensuring the final output is exhaustively validated.**