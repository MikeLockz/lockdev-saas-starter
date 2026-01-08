# Prompt: Comprehensive Backend Implementation Review

You are a Lead Backend Architect, Database Performance Specialist, and HIPAA Compliance Officer. Your task is to perform an exhaustive, line-by-line acceptance review of the `docs/09 - backend details.md` document.

This document claims to provide the technical implementation specifications for the API defined in `docs/05 - API Reference.md`, using the schema defined in `docs/04 - sql.ddl`.

**Your Goal:** Verify that `docs/09` is a complete, executable blueprint. If a junior engineer were to pick this up, they should not have to guess about SQL queries, table names, input schemata, or business logic.

## Reference Materials
*   **The Blueprint:** `docs/09 - backend details.md` (The document under review)
*   **The Contract:** `docs/05 - API Reference.md` (Source of Truth for what MUST be built)
*   **The Foundation:** `docs/04 - sql.ddl` (Source of Truth for what tables EXIST)

## Instructions

### Phase 1: Exhaustive Completeness Check
You must iterate through **every single endpoint** defined in `docs/05 - API Reference.md` and verify if it has a corresponding technical specification in `docs/09 - backend details.md`.

**Action:** Generate a Markdown table with the following rows for *every* endpoint found in the API reference (there are approx 50+).

| Endpoint | Method | Status | Schema Valid? | Logic Valid? | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/users/me` | GET | ✅ Present | ✅ Valid | ✅ Complete | **PASS** |
| `/api/appointments` | POST | ❌ MISSING | N/A | N/A | **FAIL** |
| `/api/messages` | POST | ✅ Present | ❌ Uses non-existent table `messages` | ❌ Logic assumes table exists | **FAIL** |

*   **Status in docs/09:** "Present" or "MISSING".
*   **Schema Valid?:** Does the SQL provided in `docs/09` use tables/columns that ACTUALLY exist in `docs/04`?
    *   *Critical Check:* If `docs/09` assumes a table exists (e.g. `appointments`, `messages`, `tasks`), but it is NOT in `docs/04`, mark this as ❌ **Schema Hallucination**.
*   **Logic Valid?:** Does the python pseudo-code/explanation cover the complex requirements?
    *   *Must Have:* Auth checks, Input Validation, DB Interaction, Response Construction.
*   **Pass/Fail:** PASS only if Present + Schema Valid + Logic Valid.

### Phase 2: Security & HIPAA Analysis
Review the implementation details for security flaws.
*   **Tenancy Leak:** Look at every SQL query. Is `organization_id` used in the `WHERE` clause? If missing, flag as **CRITICAL SECURITY RISK**.
*   **Broken Access Control:** Does the code check permissions? (e.g. `if role not in ['ADMIN', 'PROVIDER']: raise 403`).
*   **Audit Logging:** For sensitive endpoints (viewing patient health info, "Break Glass"), does the logic explicitly mention `INSERT INTO audit_logs`?
*   **Field Level Security:** Are we returning secure fields (like `password_hash` or `stripe_token`) in any `SELECT *`? (Flag as FAIL if so).

### Phase 3: Database Performance & Integrity
Analyze the proposed SQL for performance bottlenecks.
*   **Missing Indexes:** For every `WHERE` clause in `docs/09` (e.g. `WHERE email = ?`, `WHERE status = ?`), check `docs/04 - sql.ddl`. is there an index for that column? If not, flag as "Missing Index".
*   **N+1 Queries:** Does the logic loop through a list and perform a query inside the loop? (Flag as "Performance Risk").
*   **Transaction Boundaries:** For multi-step writes (e.g. Create Organization + Create Admin Member), is there an explicit `BEGIN` ... `COMMIT` block?

### Phase 4: Developer Usability
*   **Input/Output Schemas:** Are the Pydantic schemas named consistent with standard naming? (e.g. `UserCreate`, `UserResponse`).
*   **Pagination:** Do LIST endpoints include `:limit` and `:offset` in the SQL?
*   **Dependency Injection:** Are we correctly using `Depends(get_db)` and `Depends(get_current_user)`?

### Phase 5: Iterative Resolution
**This is a critical step.** If the review in Phases 1-4 identifies any **Critical Issues**, **Major Logic Holes**, **Schema Hallucinations**, or **Missing Endpoints**:
1.  **Resolve the Issue:** Update `docs/09 - backend details.md` (and `docs/04 - sql.ddl` if absolutely necessary and justified) to fix the problem.
2.  **Re-Run the Check:** Perform the checks again on the updated content.
3.  **Repeat:** Continue this loop until there are **NO** critical or major issues found.
4.  **Reporting:** The "Deliverables" below should reflect the *final, clean state* after your fixes. If unresolvable blocking issues remain, list them in the Critical Issues List.

## Deliverables
After your analysis, output a report with the following structure:

1.  **Executive Summary**: A high-level assessment. Is this ready for code?
2.  **Schema Gap Analysis**: A dedicated list of tables/columns that `docs/09` relies on but `docs/04` lacks.
3.  **Missing Indexes List**: A list of suggested indexes to add to `docs/04` based on the query patterns in `docs/09`.
4.  **The Exhaustive Tracking Table**: The long table generated in Phase 1.
5.  **Critical Issues List**: Any security risks, tenancy leaks, or major logic holes.
6.  **Action Plan**: Specific next steps.
7.  **Resolution Summary**: A report detailing:
    *   **Iteration Count**: How many loops it took to reach a clean state.
    *   **Issues Resolved**: A count of Critical, High, and Blocker issues fixed.
    *   **Fix Log**: A list of the specific issues found and the exact changes made to resolve them.

**Final Note to the Reviewer:** Do not be lenient. If the DDL is missing a table, fail the endpoint. If a `SELECT` statement forgets `organization_id`, fail the endpoint. Precision is key.
