# Frontend Views & Routes - Review Prompt

**Role:** Act as a Senior Frontend Architect and UX Lead with 15+ years of experience building healthcare applications with strict HIPAA compliance requirements.

**Task:** Conduct a comprehensive review of the [Frontend Views & Routes](file:///Users/mbp/Development/lockdev-saas-starter/docs/06%20-%20Frontend%20Views%20%26%20Routes.md) documentation for a multi-tenant healthcare platform.

---

## Context

- Multi-tenant healthcare SaaS with patient mobile app and provider workflows
- Primary Personas: Self-Managed Patients, Dependent Patients (no login), Proxies (manage dependents), Providers, Clinical Staff, Administrative Staff, Call Center Agents, Organization Admins, Super Admins, Auditors
- HIPAA compliant - no PHI caching, online-only PWA
- Tech stack: React, TanStack Router, Zustand, Firebase Auth (GCIP)

---

## Review Criteria

### 1. Completeness
- Are ALL user personas represented with appropriate routes?
- Are there missing CRUD routes (e.g., create patient, edit provider)?
- Are all error states and edge cases documented (auth failures, expired sessions, consent flows)?

### 2. Security & Compliance
- Do role restrictions follow the principle of least privilege?
- Is the permission matrix comprehensive and unambiguous?
- Are all PHI-accessing routes properly flagged?
- Is the "Break Glass" flow (impersonation) adequately documented?

### 3. User Experience
- Is the navigation hierarchy intuitive (dashboard → detail → sub-pages)?
- Are redirect flows clear (unauthenticated → login → consent → dashboard)?
- Are loading/empty/error states described for each route?

### 4. Technical Accuracy
- Do the documented API calls match the [API Reference](file:///Users/mbp/Development/lockdev-saas-starter/docs/05%20-%20API%20Reference.md)?
- Are URL parameter types correct (ULID vs UUID)?
- Are query parameters documented where needed?

### 5. Missing Routes
Consider whether the following are needed:
- Onboarding/first-time user flows?
- Password change vs forgot password?
- MFA setup page?
- Notification preferences detail page?
- Help/support routes?
- Appointment scheduling routes?
- Messaging/chat routes?

---

## Output Format

Provide findings in a structured Markdown table:

| Category | Finding | Severity | Recommendation |
|----------|---------|----------|----------------|
| Completeness | Example finding | Critical/High/Medium/Low | Specific fix |
| Security | ... | ... | ... |

---

## Related Documents

- [06 - Frontend Views & Routes.md](file:///Users/mbp/Development/lockdev-saas-starter/docs/06%20-%20Frontend%20Views%20%26%20Routes.md) — Document under review
- [05 - API Reference.md](file:///Users/mbp/Development/lockdev-saas-starter/docs/05%20-%20API%20Reference.md) — API endpoints
- [01 - Review prompt.md](file:///Users/mbp/Development/lockdev-saas-starter/docs/01%20-%20Review%20prompt.md) — Original requirements
