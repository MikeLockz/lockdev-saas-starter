# Story 2.6: Secure Impersonation ("Break Glass")
**User Story:** As an Admin, I want to impersonate a patient to debug issues, but with strict auditing, so that I can support users complianty.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 2.6 from `docs/03`

## Technical Specification
**Goal:** Implement "Break Glass" endpoint.

**Changes Required:**
1.  **Endpoint:** `POST /api/admin/impersonate/{patient_id}`
    - Permission: Admin only.
    - Body: `reason` (Required).
2.  **Logic:**
    - Log "Break Glass" event to `AuditLog`.
    - Generate Custom Token via Firebase Admin.
    - Add Claims: `act_as: patient_id`, `impersonator_id: admin_id`.

## Acceptance Criteria
- [ ] Only Admin can call.
- [ ] Audit log entry created.
- [ ] Returned token contains correct custom claims.

## Verification Plan
**Manual Verification:**
- Call endpoint as Admin.
- Verify Audit Log entry in DB.
- Decode returned token (jwt.io) to check claims.
