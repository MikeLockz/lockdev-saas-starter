# Story 13.1: Document Models & Migration
**User Story:** As a Developer, I want document database models, so that I can track uploaded files.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.2 from `docs/10 - application implementation plan.md`
- **DDL Ref:** `docs/04 - sql.ddl` (Lines 290-310: `documents`)

## Technical Specification
**Goal:** Create document model for file metadata.

**Changes Required:**

1.  **Migration:** `backend/migrations/versions/d5e6f7a8b9c0_create_documents_table.py`
2.  **Model:** `backend/src/models/documents.py`

## Acceptance Criteria
- [x] `Document` model has all required fields.
- [x] `s3_key` is unique.
- [x] Migration file created.
- [x] Model exported in `__init__.py`.
