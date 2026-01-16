# Epic 13: Document Management
**User Story:** As a Provider, I want to upload and manage patient documents, so that clinical records are stored securely.

**Goal:** Secure document upload to S3 with presigned URLs and document listing.

## Traceability Matrix
| Plan Step (docs/10) | Story File | Status |
| :--- | :--- | :--- |
| Step 3.2 (Models) | `story-13-01-document-models.md` | Done |
| Step 3.2 (API) | `story-13-02-document-api.md` | Done |
| Step 3.2 (Frontend) | `story-13-03-document-frontend.md` | Done |

## Execution Order
1.  [x] `story-13-01-document-models.md`
2.  [x] `story-13-02-document-api.md`
3.  [x] `story-13-03-document-frontend.md`

## Epic Verification
**Completion Criteria:**
- [x] Document model tracks file metadata.
- [x] Presigned upload URLs work correctly.
- [x] Presigned download URLs work correctly.
- [x] Document list displays in patient detail.
- [x] Files stored in S3 (Localstack for dev).
