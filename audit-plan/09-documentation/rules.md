# Documentation Audit Rules

## Scope
- `README.md` — Project overview
- `docs/` — All documentation
- `backend/src/**/*.py` — Docstrings
- `frontend/src/**/*.ts` — JSDoc comments
- `/docs`, `/redoc` — API documentation

---

## Rules

### DOC-001: README Completeness
**Severity:** 🟠 P1  
**Requirement:** README must include: purpose, quickstart, prerequisites, architecture overview.  
**Check:**
```bash
grep -E "##.*Install|##.*Getting Started|##.*Setup|##.*Quick" README.md
grep -E "##.*Architecture|##.*Overview" README.md
```

---

### DOC-002: API Documentation
**Severity:** 🟠 P1  
**Requirement:** All API endpoints must have OpenAPI documentation with descriptions and examples.  
**Check:**
```bash
grep -r "summary=\|description=" backend/src/api/
grep -r "example\|Example" backend/src/schemas/
```
**Verify:** Access `/docs` and `/redoc` endpoints.

---

### DOC-003: Code Docstrings
**Severity:** 🟡 P2  
**Requirement:** Public functions and classes must have docstrings.  
**Check:**
```bash
# Find functions without docstrings (basic check)
grep -rA1 "def [a-z_]*(" backend/src/ | grep -B1 "^--$" | head -20
```
**Tools:** `pydocstyle`, `interrogate`

---

### DOC-004: Architecture Documentation
**Severity:** 🟡 P2  
**Requirement:** System architecture must be documented with diagrams (C4, sequence, ERD).  
**Check:**
```bash
ls docs/architecture/ docs/*.d2 docs/*.dsl docs/*.puml 2>/dev/null
find docs -name "*.png" -o -name "*.svg" 2>/dev/null
```

---

### DOC-005: Environment Setup Guide
**Severity:** 🟠 P1  
**Requirement:** Development environment setup must be documented step-by-step.  
**Check:**
```bash
grep -l "docker\|make\|pnpm\|uv" docs/*.md README.md
grep -E "prerequisites|requirements" -i docs/*.md README.md
```

---

### DOC-006: Runbook/Playbook
**Severity:** 🟠 P1  
**Requirement:** Operational runbooks must exist for common incidents.  
**Scenarios:** Deploy rollback, database recovery, security incident response  
**Check:**
```bash
ls docs/runbook/ docs/playbook/ docs/operations/ 2>/dev/null
grep -ri "rollback\|incident\|recovery" docs/
```

---

### DOC-007: Changelog Maintenance
**Severity:** 🟡 P2  
**Requirement:** User-facing changes must be documented in CHANGELOG.md.  
**Format:** Keep a Changelog (https://keepachangelog.com)  
**Check:**
```bash
cat CHANGELOG.md 2>/dev/null | head -30
grep -E "##.*\[.*\]|Added|Changed|Fixed" CHANGELOG.md
```

---

### DOC-008: Decision Records (ADRs)
**Severity:** 🟢 P3  
**Requirement:** Significant architectural decisions should be documented as ADRs.  
**Check:**
```bash
ls docs/adr/ docs/decisions/ 2>/dev/null
find docs -name "*.md" -exec grep -l "Status.*Accepted\|Decision\|Context" {} \;
```

---

### DOC-009: Inline Code Comments
**Severity:** 🟢 P3  
**Requirement:** Complex logic must have explanatory comments.  
**Anti-Pattern:**
```bash
# Find large functions without comments
grep -c "#" backend/src/services/*.py
```

---

### DOC-010: Deprecation Notices
**Severity:** 🟡 P2  
**Requirement:** Deprecated APIs/features must be marked with deprecation warnings.  
**Check:**
```bash
grep -r "deprecated\|Deprecated\|@deprecated" backend/src/ frontend/src/
grep -r "warnings.warn" backend/src/
```
