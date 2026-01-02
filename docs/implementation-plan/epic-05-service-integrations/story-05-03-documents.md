# Story 5.3: Document Processing (AWS Textract)
**User Story:** As a User, I want to upload documents and have them automatically processed, so that I don't have to manualy enter data.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 5.3 from `docs/03`

## Technical Specification
**Goal:** Async document processing pipeline.

**Changes Required:**
1.  **API:** `generate_upload_url`.
2.  **Worker:** `process_document_job`.
    - Fetch file from S3.
    - Call AWS Textract.
    - Store results in DB.

## Acceptance Criteria
- [x] Upload URL allows file upload.
- [x] Worker processes file and saves text.

## Verification Plan
**Manual Verification:**
- Upload image. Check DB for extracted text after worker run.
