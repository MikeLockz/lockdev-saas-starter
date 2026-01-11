# Story 1.1: Initialize Monorepo Structure
**User Story:** As a Developer, I want a clean monorepo structure with git initialized, so that I can organize backend, frontend, and infrastructure code.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 1.1 from `docs/03`

## Technical Specification
**Goal:** Initialize the project root with the required directory structure.

**Changes Required:**
1.  **Directories:**
    - `apps/backend/src`, `backend/tests`
    - `apps/frontend/src`
    - `contracts`
    - `.github/workflows`
    - `infra`
2.  **Files:**
    - `Makefile` (Empty for now)
    - `.gitignore` (Standard Python + Node + macOS + IntelliJ/VSCode)
3.  **Git:**
    - Initialize `git init` (if not already done).

## Acceptance Criteria
- [ ] Directory structure matches specification.
- [ ] `.gitignore` is present and includes standard patterns.
- [ ] Git repository is initialized.

## Verification Plan
**Manual Verification:**
- Command: `ls -R`
- Expected Output: Listing shows `backend`, `frontend`, `infra`, `.gitignore`.
