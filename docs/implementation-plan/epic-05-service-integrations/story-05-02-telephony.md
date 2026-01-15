# Story 5.2: Telephony & Messaging (AWS)
**User Story:** As a Patient, I want to receive SMS reminders, so that I don't miss appointments.

## Status
- [x] **Complete**

## Context
- **Roadmap Ref:** Step 5.2 from `docs/03`

## Technical Specification
**Goal:** Integrate AWS Pinpoint/Connect.

**Changes Required:**
1.  **File:** `backend/src/services/telephony.py`
    - `send_sms(to, body)` via AWS Pinpoint.
    - `initiate_outbound_call(to, flow_id)` via Amazon Connect.
    - **Safety:** Mask phone numbers in logs.

## Acceptance Criteria
- [x] `send_sms` sends message (verified via AWS console/logs).
- [x] Logs show masked phone numbers.

## Verification Plan
**Manual Verification:**
- Trigger SMS to own number (if sandbox access available).
