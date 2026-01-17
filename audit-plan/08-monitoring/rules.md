# Monitoring & Observability Audit Rules

## Scope
- `backend/src/main.py` — Sentry initialization
- `backend/src/logging.py` — Structlog config
- `infra/aws/` — CloudWatch, SES for alerts
- `.github/workflows/` — CI alerting

## Available Tools
- **Error Tracking:** Sentry (only 3rd party monitoring tool)
- **Logging:** Structlog → CloudWatch
- **Alerting:** Email via AWS SES

---

## Rules

### MON-001: Sentry Integration
**Severity:** 🟠 P1  
**Requirement:** Sentry must be configured for error tracking, APM, and distributed tracing.  
**Check:**
```bash
grep -r "sentry_sdk\|SENTRY_DSN" backend/src/main.py backend/src/config.py
grep -r "FastApiIntegration\|SqlalchemyIntegration" backend/src/main.py
```
**Expected:** Sentry SDK initialized with FastAPI and SQLAlchemy integrations.

---

### MON-002: Sentry Environment Configuration
**Severity:** 🟡 P2  
**Requirement:** Sentry must be configured with environment tags and proper sampling.  
**Check:**
```bash
grep -r "environment\|traces_sample_rate\|profiles_sample_rate" backend/src/main.py
```
**Expected:** Environment set from config, sample rates configured (e.g., 10% for traces).

---

### MON-003: Sentry PII Protection
**Severity:** 🔴 P0  
**Requirement:** Sentry must NOT send PII (HIPAA compliance).  
**Check:**
```bash
grep -r "send_default_pii" backend/src/main.py
```
**Expected:** `send_default_pii=False`

---

### MON-004: Structured Logging
**Severity:** 🟠 P1  
**Requirement:** Logs must be structured (JSON) with consistent fields.  
**Required Fields:** `timestamp`, `level`, `message`, `request_id`, `user_id` (if authenticated)  
**Check:**
```bash
grep -r "structlog\|JSONRenderer" backend/src/logging.py
grep -r "logger\." backend/src/api/ | head -10
```

---

### MON-005: Log Levels
**Severity:** 🟡 P2  
**Requirement:** Appropriate log levels must be used (DEBUG/INFO/WARNING/ERROR/CRITICAL).  
**Anti-Pattern:**
```bash
# Should NOT find print statements in production code
grep -r "print(" backend/src/ --include="*.py" | grep -v test | grep -v __pycache__
```

---

### MON-006: Request Tracing
**Severity:** 🟠 P1  
**Requirement:** All requests must have correlation IDs propagated to Sentry and logs.  
**Check:**
```bash
grep -r "X-Request-ID\|request_id\|trace_id" backend/src/middleware/
grep -r "set_tag.*request_id" backend/src/
```

---

### MON-007: Health Check Endpoints
**Severity:** 🟠 P1  
**Requirement:** Services must expose `/health` (shallow) and `/health/deep` (dependencies).  
**Check:**
```bash
grep -r "/health" backend/src/main.py
```
**Expected:** Both shallow (web server up) and deep (DB/Redis connected) checks.

---

### MON-008: Email Alerting Configuration
**Severity:** � P1  
**Requirement:** Critical failures must trigger email alerts via AWS SES.  
**Check:**
```bash
grep -r "SES\|email\|alert" infra/aws/
grep -r "send_email\|smtp" backend/src/services/
```
**Integration:** Sentry can send alert emails directly, or via SES webhook.

---

### MON-009: Sentry Alert Rules
**Severity:** 🟠 P1  
**Requirement:** Sentry must have alert rules configured for critical errors.  
**Manual Check:** Verify in Sentry Dashboard:
- Alert on new issues
- Alert on error rate spikes
- Email notification action configured

---

### MON-010: Database Query Monitoring
**Severity:** � P1  
**Requirement:** Slow queries must be logged and captured in Sentry.  
**Check:**
```bash
grep -r "SqlalchemyIntegration" backend/src/main.py
grep -r "slow_query\|log_min_duration" backend/src/database.py
```

---

### MON-011: SLO/SLA Definitions
**Severity:** � P2  
**Requirement:** Critical services must have defined SLOs (availability, latency).  
**Documentation Check:**
```bash
ls docs/slo*.md docs/sla*.md 2>/dev/null
grep -ri "availability\|latency.*ms\|99\.*%" docs/
```
**Targets:** 99.9% availability, p95 latency < 500ms

---

### MON-012: Resource Utilization Monitoring
**Severity:** 🟡 P2  
**Requirement:** CPU, memory, and connection pool usage must be monitored.  
**Check:**
```bash
grep -r "memory\|cpu\|pool" backend/src/
```
**Note:** Basic resource monitoring available via Sentry APM, detailed via CloudWatch.
