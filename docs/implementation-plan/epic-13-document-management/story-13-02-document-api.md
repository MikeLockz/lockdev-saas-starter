# Story 13.2: Document API (S3 Presigned URLs)
**User Story:** As a Provider, I want to upload and download documents securely without exposing S3 credentials.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.2 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "Documents")
- **Existing:** S3 service exists in `backend/src/services/documents.py`

## Technical Specification
**Goal:** Implement presigned URL generation and document CRUD.

**Changes Required:**

1.  **Schemas:** `backend/src/schemas/documents.py`
2.  **API Router:** `backend/src/api/documents.py` (Updated with org/patient scoping)

## Acceptance Criteria
- [x] Upload URL endpoint returns presigned PUT URL.
- [x] Confirm endpoint marks document as uploaded.
- [x] Download URL endpoint returns presigned GET URL.
- [x] Document list returns all patient documents.
- [x] Delete endpoint soft-deletes documents.
