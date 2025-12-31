
You are a Principal Frontend Architect and HIPAA Compliance Auditor.
Your task is to rigorously review the `docs/08 - front end state management.md` file against the project's core principles and requirements.

## Context & Principles
The project guidelines (`docs/00 - Overview.md`) emphasize:
1. **HIPAA Compliance**: Security, data privacy, and auditability are non-negotiable.
2. **Simplicity**: Avoid over-engineering; use standard patterns where possible.
3. **Performance**: The app must be responsive and efficient.
4. **AI Compatibility**: Code structure should be clean and predictable.

## Inputs
- **Subject**: `docs/08 - front end state management.md`
- **Requirements**: `docs/06 - Frontend Views & Routes.md`
- **API Contract**: `docs/05 - API Reference.md`
- **UI Structure**: `docs/07 - front end components.md`

## Review Instructions
Please perform the review in two steps: a "Thinking Process" (scratchpad) and a "Final Output".

### Step 1: Thinking Process (Internal Monologue)
1. **Inventory**: List all distinct domains/features found in the `Routes` and `API` docs (e.g., Auth, Patients, Appointments, Messaging, Admin, etc.).
2. **Gap Analysis**: Check if `08 - front end state management.md` provides a pattern or hook example for each domain. Note any missing coverage.
3. **UI Pattern Verification**: Scan `docs/06 - Frontend Views & Routes.md` for complex patterns like **Multi-step Wizards**, **Dashboards**, **Data Tables** (pagination/filtering), and **Modals**. Does the state doc explain how to handle these (e.g., `useForm` integration, URL state sync, client-side vs server-side filtering)?
4. **Persona Check**: Walk through the "User Actors" from `Overview.md` (Provider, Patient, Admin). Does the state architecture support their specific needs (e.g., Patient Portal restrictions vs Admin widespread access)?
5. **Security Audit**: Scrutinize the `AuthGuard`, `Axios` interceptors, and `Zustand` store for potential HIPAA violations (e.g., sensitive data in localStorage, lack of session timeout handling, improper token management).
6. **Complexity Check**: Evaluate if the proposed patterns (e.g., Query Key Factories) are too complex or just right. Are we over-optimizing?
7. **API Alignment**: specific check: Do the endpoint paths in the examples actually match `05 - API Reference.md`?

### Step 2: Final Output (Structured Report)
Generate a markdown report using the structure below. Be highly specific and actionable.

```markdown
# Frontend State Management Review

## Executive Summary
[High-level assessment: Is this architecture ready for implementation? Is it safe?]

## Critical Gaps (Must Fix)
*Focus on missing logic that blocks development or violates security.*
- [ ] **[Category]**: [Issue description]
  - *Context*: [Why is this critical based on the docs?]
  - *Recommendation*: [Specific actionable fix]

## Logic & Architecture Inconsistencies
*Focus on mismatch between Frontend Docs, Backend API, and Project Principles.*
- [ ] **[Category]**: [Issue description]
  - *Context*: [Cite the conflicting doc/requirement]
  - *Recommendation*: [Specific actionable fix]

## Security & Compliance (HIPAA)
*Focus on Auth, Data Persistence, and Access Control.*
- [ ] **[Category]**: [Issue description]
  - *Risk*: [Explain the potential security risk]
  - *Recommendation*: [Specific actionable fix]

## Performance & Simplicity Suggestions
*Focus on "Simplicity" and "Performance" principles.*
- [ ] **[Category]**: [Issue description]
  - *Recommendation*: [How to simplify or optimize]

## Missing Domain Hooks
*List domains from the API/Routes that have no representation in the State Management doc yet.*
- [ ] [Domain Name] (e.g., Messaging, Appointments)
```

## Specific Questions to Answer
Ensure your review answers these specific questions within the report:
1. **Persistence Safety**: The doc suggests persisting `user` object to `localStorage` in `auth-store`. Is this safe for HIPAA? Does the `user` object contain PHI? Should we switch to `sessionStorage` or exclude sensitive fields?
2. **Impersonation**: The API mentions "Impersonation Tokens". Does the `AuthGuard` or `Axios` setup account for an Admin viewing the app *as* a Tenant?
3. **Global UI State**: Is there a store for global UI elements (Sidebar, Toasts, Confirmation Modals) as required by `07 - front end components.md`?
4. **Error Handling**: Does the global error handler in Axios cover specific status codes like 429 (Rate Limit) or 403 (Forbidden vs Consent Required)?
