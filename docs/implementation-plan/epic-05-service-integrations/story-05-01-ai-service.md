# Story 5.1: AI Service (Vertex AI)
**User Story:** As a User, I want AI-powered summaries, so that I can quickly understand complex data.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 5.1 from `docs/03`

## Technical Specification
**Goal:** Integrate Google Vertex AI (Gemini).

**Changes Required:**
1.  **File:** `backend/src/services/ai.py`
    - Initialize `vertexai` client.
    - Implement `summarize_text(text: str)` using `gemini-1.5-pro`.
    - Enforce JSON response schema using Pydantic.
    - **Compliance:** Ensure "Zero Retention" config.

## Acceptance Criteria
- [x] Service returns valid JSON summary.
- [x] Unit tests mock the API call successfully.

## Verification Plan
**Automated Tests:**
- Test with mock client response.
