# Code Quality Audit Rules

## Scope
- `backend/src/` — Python code
- `frontend/src/` — TypeScript code
- `biome.json`, `pyproject.toml` — Linter configs

---

## Rules

### CQ-001: Linting Enabled
**Severity:** 🟠 P1  
**Requirement:** Linting must be configured and passing.  
**Tools:** Ruff (Python), Biome (TS/JS)  
**Check:**
```bash
grep -r "ruff\|biome" .pre-commit-config.yaml Makefile .github/workflows/
```
**Run:** `make lint` must pass.

---

### CQ-002: Type Checking
**Severity:** 🟠 P1  
**Requirement:** Static type checking must be enabled and passing.  
**Check:**
```bash
grep -r "mypy\|pyright" backend/pyproject.toml Makefile
grep -r "tsc\|--noEmit" frontend/package.json Makefile
```
**Run:** `make typecheck` must pass.

---

### CQ-003: Code Formatting
**Severity:** 🟡 P2  
**Requirement:** Code must be consistently formatted (automated on commit).  
**Check:**
```bash
grep -r "format\|ruff-format\|biome format" .pre-commit-config.yaml Makefile
```

---

### CQ-004: Cyclomatic Complexity
**Severity:** 🟡 P2  
**Requirement:** Functions must not exceed complexity threshold (max 10).  
**Check:**
```bash
grep -r "complexity\|max-complexity\|C901" backend/pyproject.toml biome.json
```
**Tools:** Ruff (`C901`), ESLint complexity rule

---

### CQ-005: Function Length
**Severity:** 🟡 P2  
**Requirement:** Functions should not exceed 50 lines.  
**Check:**
```bash
# Find long functions (basic heuristic)
grep -n "def " backend/src/ -r | wc -l
```
**Tools:** Ruff, pylint

---

### CQ-006: Dead Code Detection
**Severity:** 🟡 P2  
**Requirement:** Unused imports, variables, and functions must be removed.  
**Check:**
```bash
grep -r "F401\|F841\|unused" backend/pyproject.toml biome.json
```
**Tools:** Ruff (`F401`, `F841`), Biome noUnusedVariables

---

### CQ-007: Code Duplication
**Severity:** 🟡 P2  
**Requirement:** Significant code duplication must be refactored.  
**Threshold:** No duplicate blocks > 10 lines  
**Check:**
```bash
grep -r "duplicate\|copy-paste" .github/workflows/
```
**Tools:** jscpd, pylint

---

### CQ-008: Import Organization
**Severity:** 🟢 P3  
**Requirement:** Imports must be organized (stdlib → third-party → local).  
**Check:**
```bash
grep -r "isort\|I001" backend/pyproject.toml .pre-commit-config.yaml
grep -r "organizeImports" biome.json
```

---

### CQ-009: Consistent Naming
**Severity:** 🟡 P2  
**Requirement:** Naming conventions must be consistent.  
**Conventions:**
- Python: `snake_case` for functions/variables, `PascalCase` for classes
- TypeScript: `camelCase` for functions/variables, `PascalCase` for components/types
**Check:**
```bash
grep -r "naming-convention\|N8" backend/pyproject.toml
```

---

### CQ-010: Magic Numbers/Strings
**Severity:** 🟢 P3  
**Requirement:** Magic numbers and strings should be constants.  
**Anti-Pattern:**
```bash
grep -rE "if.*==[^=]*[0-9]{2,}|status.*==[^=]*[0-9]" backend/src/api/
```
**Expected:** Use named constants or enums.

---

### CQ-011: Error Handling Patterns
**Severity:** 🟠 P1  
**Requirement:** Exceptions must be specific (no bare `except:`).  
**Check:**
```bash
grep -r "except:" backend/src/ --include="*.py"
grep -r "catch\s*{" frontend/src/ --include="*.ts"
```
**Expected:** Catch specific exception types.

---

### CQ-012: TODO/FIXME Tracking
**Severity:** 🟢 P3  
**Requirement:** TODO/FIXME comments must be tracked and have associated issues.  
**Check:**
```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" backend/src/ frontend/src/ | head -20
```
