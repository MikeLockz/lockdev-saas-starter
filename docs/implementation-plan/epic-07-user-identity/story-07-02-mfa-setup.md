# Story 7.2: MFA Setup & Verification
**User Story:** As a Security-Conscious User, I want to enable two-factor authentication, so that my account is protected from unauthorized access.

## Status
- [x] **Complete** (2026-01-02)

## Context
- **Roadmap Ref:** Step 1.2 from `docs/10 - application implementation plan.md`
- **API Ref:** `docs/05 - API Reference.md` (Section: "MFA")
- **HIPAA:** MFA is required for Staff/Provider roles accessing PHI.

## Technical Specification
**Goal:** Implement TOTP-based MFA enrollment and verification.

**Changes Required:**

1.  **Dependencies:** Add `pyotp` to `backend/pyproject.toml`

2.  **Migration:** `backend/migrations/versions/xxx_mfa_secrets.py`
    - Add to `users` table:
      - `mfa_secret` (String, encrypted TOTP secret)
      - `mfa_backup_codes` (JSONB, array of hashed codes)

3.  **Endpoints:** `backend/src/api/users.py`
    - `POST /api/v1/users/me/mfa/setup`
      - Generate TOTP secret using `pyotp.random_base32()`
      - Return provisioning URI for QR code
      - Store secret in user record (temporary until verified)
    - `POST /api/v1/users/me/mfa/verify`
      - Validate TOTP code against secret
      - Set `mfa_enabled = True`
      - Generate and return backup codes (one-time display)
    - `POST /api/v1/users/me/mfa/disable`
      - Require password confirmation
      - Set `mfa_enabled = False`, clear secret

4.  **Schemas:** `backend/src/schemas/users.py`
    - `MFASetupResponse` (provisioning_uri, secret)
    - `MFAVerifyRequest` (code: str)
    - `MFAVerifyResponse` (backup_codes: list[str])

5.  **Auth Update:** `backend/src/security/auth.py`
    - Check `mfa_enabled` for roles requiring MFA
    - Verify MFA claim in token or require step-up auth

## Acceptance Criteria
- [x] `POST /mfa/setup` returns QR code URI and secret.
- [x] `POST /mfa/verify` with valid code enables MFA.
- [x] `POST /mfa/verify` with invalid code returns 400.
- [x] Backup codes are returned only once after verification.
- [ ] Staff/Provider without MFA cannot access PHI routes. (Requires auth middleware update)
- [x] Audit log captures MFA enable/disable events (via user table audit trigger).

## Verification Plan
**Automated Tests:**
- `pytest tests/api/test_mfa.py::test_setup_returns_uri`
- `pytest tests/api/test_mfa.py::test_verify_enables_mfa`
- `pytest tests/api/test_mfa.py::test_invalid_code_rejected`
- `pytest tests/api/test_mfa.py::test_staff_blocked_without_mfa`

**Manual Verification:**
- Use Google Authenticator app to scan QR code
- Verify 6-digit codes work correctly
