# Frontend Audit Rules

## Scope
- `frontend/src/` — React application code
- `frontend/vite.config.ts` — Build and PWA config
- `frontend/src/lib/` — Axios, Firebase, utilities

---

## Rules

### FE-001: No PHI in Client Storage
**Severity:** 🔴 P0  
**Requirement:** PHI must NOT be stored in localStorage, sessionStorage, or IndexedDB.  
**Rationale:** Client-side storage is not encrypted and persists after logout.  
**Check:**
```bash
grep -rE "localStorage\.(set|get)Item\(.*patient\|.*medical\|.*health" frontend/src/
grep -rE "sessionStorage\.(set|get)Item\(.*patient\|.*medical" frontend/src/
grep -r "indexedDB\|IDBDatabase" frontend/src/
```
**Expected:** No matches for PHI-related storage. Only auth tokens (short-lived) allowed.

---

### FE-002: PWA Caching Strategy
**Severity:** 🔴 P0  
**Requirement:** Service worker must use `NetworkOnly` for all `/api/*` routes.  
**Rationale:** Prevents caching of PHI responses.  
**Check:**
```bash
grep -r "NetworkOnly" frontend/vite.config.ts
grep -r "runtimeCaching" frontend/vite.config.ts
grep -r "navigateFallbackDenylist.*api" frontend/vite.config.ts
```
**Expected:** API routes excluded from all caching.

---

### FE-003: Firebase Config Exposure
**Severity:** 🟡 P2  
**Requirement:** Firebase client config should only contain PUBLIC keys (apiKey, authDomain, projectId). No service account keys.  
**Check:**
```bash
grep -r "FIREBASE\|firebase" frontend/src/lib/firebase.ts
grep -r "private_key\|client_email" frontend/
```
**Expected:** Only public config keys. No private keys.

---

### FE-004: Route Protection
**Severity:** 🟠 P1  
**Requirement:** Protected routes must check auth state before rendering. No flash of protected content.  
**Check:**
```bash
grep -r "useAuth\|isAuthenticated\|ProtectedRoute" frontend/src/routes/
grep -r "redirect.*login\|Navigate.*login" frontend/src/
```
**Expected:** Auth check with loading state, redirect for unauthenticated users.

---

### FE-005: Axios Domain Whitelist
**Severity:** 🔴 P0  
**Requirement:** Axios interceptor must validate all request URLs against domain whitelist.  
**Check:**
```bash
grep -r "ALLOWED_DOMAINS" frontend/src/lib/axios.ts
grep -r "interceptors.request" frontend/src/lib/axios.ts
```
**Expected:** Request interceptor blocking non-whitelisted domains.

---

## General Best Practices

### FE-006: Accessibility (a11y)
**Severity:** 🟠 P1  
**Requirement:** UI must meet WCAG 2.1 AA standards (semantic HTML, ARIA labels, keyboard nav).  
**Check:**
```bash
grep -r "aria-\|role=\|tabIndex" frontend/src/components/
grep -r "alt=\|<label" frontend/src/
```
**Tools:** Run `pnpm exec axe` or browser DevTools Lighthouse.

---

### FE-007: Content Security Policy (CSP)
**Severity:** 🟠 P1  
**Requirement:** CSP headers must restrict script/style sources to prevent XSS.  
**Check:**
```bash
grep -r "Content-Security-Policy\|CSP" frontend/ backend/src/main.py
grep -r "unsafe-inline\|unsafe-eval" frontend/
```
**Expected:** No `unsafe-inline` or `unsafe-eval` in production.

---

### FE-008: Error Boundaries
**Severity:** 🟡 P2  
**Requirement:** React components must have error boundaries to prevent cascading failures.  
**Check:**
```bash
grep -r "ErrorBoundary\|componentDidCatch" frontend/src/
```

---

### FE-009: Performance Budgets
**Severity:** 🟡 P2  
**Requirement:** Bundle sizes must be monitored with defined limits.  
**Check:**
```bash
grep -r "bundlesize\|budget\|analyzer" frontend/package.json frontend/vite.config.ts
```
**Targets:** JS < 200KB gzipped, CSS < 50KB gzipped

---

### FE-010: Loading States
**Severity:** 🟡 P2  
**Requirement:** All async operations must show loading indicators (no blank screens).  
**Check:**
```bash
grep -r "isLoading\|isPending\|Skeleton\|Spinner" frontend/src/
```

---

### FE-011: Form Validation
**Severity:** 🟠 P1  
**Requirement:** All forms must have client-side validation with clear error messages.  
**Check:**
```bash
grep -r "useForm\|zodResolver\|yupResolver" frontend/src/
grep -r "error\|invalid\|required" frontend/src/components/
```
