# Story 13.3: Document Frontend
**User Story:** As a Provider, I want a UI to upload and view patient documents.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 3.2 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/patients/:id/documents`)

## Technical Specification
**Goal:** Implement document upload and listing UI.

**Changes Required:**

1.  **Components:** `frontend/src/components/documents/`
    - `FileUploader.tsx` - Drag-and-drop with S3 upload
    - `DocumentList.tsx` - Table with download/delete actions

2.  **Hooks:** `frontend/src/hooks/api/usePatientDocuments.ts`

3.  **Integration:** Documents tab added to PatientDetail page

## Acceptance Criteria
- [x] Dropzone accepts valid file types.
- [x] Upload shows progress indicator.
- [x] Uploaded document appears in list.
- [x] Download button opens file in new tab.
- [x] Delete removes document from list.
