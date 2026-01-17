# Compliance Audit Rules (HIPAA/TCPA)

## Scope
- `backend/src/models/consent.py` — Consent models
- `backend/src/api/` — API endpoints
- `backend/src/middleware/audit.py` — Audit middleware
- `backend/src/services/` — SMS, email services

---

## Rules

### COMP-001: HIPAA Consent Tracking
**Severity:** 🔴 P0  
**Requirement:** All users must sign ToS and HIPAA consent documents before accessing the application.  
**Models Required:** `ConsentDocument`, `UserConsent`  
**Check:**
```bash
grep -r "ConsentDocument\|UserConsent" backend/src/models/
grep -r "verify_latest_consents" backend/src/security/ backend/src/middleware/
```
**Expected:** Middleware/dependency blocking API access until critical consents are signed.

---

### COMP-002: TCPA SMS Consent
**Severity:** 🔴 P0  
**Requirement:** SMS messages must only be sent to users who have explicitly opted in (`communication_consent_sms = True`).  
**Check:**
```bash
grep -r "communication_consent_sms" backend/src/models/
grep -r "consent" backend/src/services/telephony.py backend/src/services/sms.py
```
**Expected:** Consent check before `send_sms()` call for non-emergency messages.

---

### COMP-003: PHI Read Access Auditing
**Severity:** 🔴 P0  
**Requirement:** All Staff read access to PHI must be logged to `audit_logs`.  
**Endpoints:** `GET /api/staff/*`, `GET /api/patients/*`  
**Check:**
```bash
grep -r "AuditMiddleware\|audit" backend/src/middleware/
grep -r "READ_ACCESS" backend/src/
```
**Expected:** Middleware intercepting Staff requests and logging to audit service.

---

### COMP-004: Break-Glass Impersonation Logging
**Severity:** 🔴 P0  
**Requirement:** Impersonation events must be logged with reason BEFORE token generation.  
**Endpoint:** `POST /admin/impersonate/{patient_id}`  
**Check:**
```bash
grep -r "impersonate" backend/src/api/admin.py
grep -r "Break Glass\|break_glass\|impersonat" backend/src/
```
**Expected:** 
1. Verify caller is ADMIN
2. Log "Break Glass" event with `reason` to audit_logs
3. Generate custom token with `act_as` and `impersonator_id` claims

---

### COMP-005: Safe Contact Protocol
**Severity:** 🟠 P1  
**Requirement:** Automated messages/voicemails must NOT be sent to contacts marked `is_safe_for_voicemail = False`.  
**Rationale:** Patient safety (e.g., domestic violence situations).  
**Check:**
```bash
grep -r "is_safe_for_voicemail" backend/src/models/
grep -r "safe_for_voicemail\|safe_contact" backend/src/services/
```
**Expected:** Check in telephony/SMS service before sending messages.

---

## General Best Practices

### COMP-006: Data Retention Policy Enforcement
**Severity:** 🟠 P1  
**Requirement:** Data must be automatically archived/deleted according to defined retention periods.  
**Check:**
```bash
grep -r "retention\|archive\|purge" backend/src/
grep -r "created_at.*<\|timedelta" backend/src/services/
```
**Documentation:** Verify `docs/` contains data retention policy document.

---

### COMP-007: Right to Deletion (GDPR/CCPA)
**Severity:** 🟠 P1  
**Requirement:** System must support user data deletion requests while maintaining legal audit trails.  
**Check:**
```bash
grep -r "delete_user\|anonymize\|forget" backend/src/
grep -r "DELETE.*user\|soft_delete" backend/src/api/
```
**Expected:** Anonymization of PII while preserving audit records.

---

### COMP-008: Data Export Capability
**Severity:** 🟡 P2  
**Requirement:** Users must be able to export their personal data (data portability).  
**Check:**
```bash
grep -r "export\|download.*data" backend/src/api/
```

---

### COMP-009: Backup Verification
**Severity:** 🟠 P1  
**Requirement:** Database backups must be tested for restore capability.  
**Check:**
```bash
grep -r "backup\|restore" infra/ .github/workflows/
```
**Documentation:** Verify backup/restore procedure exists in `docs/`.

---

### COMP-010: Audit Log Immutability
**Severity:** 🔴 P0  
**Requirement:** Audit logs must be immutable (no UPDATE/DELETE) and tamper-evident.  
**Check:**
```bash
grep -r "INSERT ONLY\|NO DELETE\|NO UPDATE" backend/migrations/
```
**Expected:** Audit table with DELETE/UPDATE disabled via RLS or triggers.
