# Testing Audit Rules

## Scope
- `backend/tests/` — Python tests
- `frontend/src/**/*.test.ts` — Frontend tests
- `frontend/playwright/` — E2E tests
- `pytest.ini`, `vitest.config.ts`, `playwright.config.ts`

---

## Rules

### TEST-001: Test Coverage Thresholds
**Severity:** 🟠 P1  
**Requirement:** Code coverage must meet minimum thresholds.  
**Thresholds:**
- Backend: ≥80% line coverage
- Frontend: ≥70% line coverage
- Critical paths (auth, billing): ≥90% branch coverage
**Check:**
```bash
grep -r "coverage\|--cov" backend/pyproject.toml Makefile
grep -r "coverage" frontend/vitest.config.ts
```

---

### TEST-002: Test Isolation
**Severity:** 🟠 P1  
**Requirement:** Tests must not share state or depend on execution order.  
**Check:**
```bash
# Look for shared state anti-patterns
grep -r "global\|class.*State\|_cache\s*=" backend/tests/
grep -r "beforeAll.*db\|afterAll.*db" frontend/src/
```
**Expected:** Each test sets up and tears down its own fixtures.

---

### TEST-003: Database Test Fixtures
**Severity:** 🟠 P1  
**Requirement:** Tests must use isolated database transactions (rollback after each test).  
**Check:**
```bash
grep -r "fixture\|@pytest.fixture" backend/tests/conftest.py
grep -r "rollback\|SAVEPOINT" backend/tests/
```

---

### TEST-004: Mock External Services
**Severity:** 🟠 P1  
**Requirement:** Tests must mock external APIs (Firebase, AWS, Stripe) to avoid network calls.  
**Check:**
```bash
grep -r "mock\|Mock\|patch\|MagicMock" backend/tests/
grep -r "vi.mock\|jest.mock" frontend/src/
```
**Anti-Pattern:**
```bash
# These should NOT appear in test files
grep -r "httpx.get\|requests.post" backend/tests/ --include="*.py"
```

---

### TEST-005: E2E Test Data Seeding
**Severity:** 🟡 P2  
**Requirement:** E2E tests must have deterministic seed data, reset before each run.  
**Check:**
```bash
grep -r "seed\|fixture" frontend/playwright.config.ts
ls backend/scripts/seed*.py 2>/dev/null
```

---

### TEST-006: Flaky Test Detection
**Severity:** 🟡 P2  
**Requirement:** CI must detect and quarantine flaky tests.  
**Check:**
```bash
grep -r "retry\|flaky\|rerun" .github/workflows/ pytest.ini
```

---

### TEST-007: Test Naming Conventions
**Severity:** 🟢 P3  
**Requirement:** Tests must follow naming convention: `test_<action>_<expected_result>`.  
**Check:**
```bash
grep -r "def test_" backend/tests/ | head -20
grep -r "it\(.*should\|describe" frontend/src/
```

---

### TEST-008: Security Test Cases
**Severity:** 🟠 P1  
**Requirement:** Tests must cover security scenarios (auth bypass, injection, IDOR).  
**Check:**
```bash
grep -r "unauthorized\|forbidden\|403\|401" backend/tests/
grep -r "injection\|xss\|csrf" backend/tests/
```

---

### TEST-009: Performance Regression Tests
**Severity:** 🟡 P2  
**Requirement:** Critical endpoints must have performance benchmarks.  
**Check:**
```bash
grep -r "benchmark\|duration\|time" backend/tests/
grep -r "@pytest.mark.slow" backend/tests/
```

---

### TEST-010: Contract Tests
**Severity:** 🟡 P2  
**Requirement:** API contracts between frontend/backend must be tested.  
**Check:**
```bash
grep -r "openapi\|schema\|pact" backend/tests/ frontend/src/
```
