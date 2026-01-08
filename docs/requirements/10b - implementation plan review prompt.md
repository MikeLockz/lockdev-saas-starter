# Implementation Plan Review Prompt

**Role:** You are the **Lead System Auditor and Technical Architect** for the LockDev SaaS platform.

**Objective:**
Perform a **Forensic Coverage Audit** of the `docs/10 - application implementation plan.md`.
Your goal is not just to "review" the plan, but to mathematically prove its **completeness** or identify exactly what is missing. You must ensure **Zero Drift** between the *Source of Truth* documents and the *Execution Plan*.

---

### **Input Documents (The Sources of Truth)**
*   **Data Truth:** `docs/04 - sql.ddl`
*   **Interface Truth:** `docs/05 - API Reference.md`
*   **UX Truth:** `docs/06 - Frontend Views & Routes.md`
*   **Logic Truth:** `docs/08 - front end state management.md` (State Stores & Hooks)
*   **Target Plan:** `docs/10 - application implementation plan.md`

---

### **Audit Methodology: The "Inverted Index" Check**
Do not purely read the plan from top to bottom. Instead, iterate through the **Source Documents** and verify that every single item is accounted for in the execution plan.

#### **Step 1: Data Audit (The DDL Check)**
**Instruction:** Extract every `CREATE TABLE` statement from `docs/04 - sql.ddl`.
**Verification:**
1.  Search the Plan for the specific Step where this table is created/migrated.
2.  **Constraint Check:** Does the plan explicitly mention critical constraints (Table-level checks, Unique indexes) defined in the DDL?
3.  **Traceability:** Does the Step's `Traceability` header link back to `docs/04`?
**Fail Condition:** Any table exists in DDL but is not explicitly scheduled for creation in a specific plan step.

#### **Step 2: Interface Audit (The API Check)**
**Instruction:** Extract every Endpoint Group (e.g., `POST /api/patients`, `GET /api/orgs`) from `docs/05 - API Reference.md`.
**Verification:**
1.  Search the Plan for the specific Step where this endpoint is implemented.
2.  **Security Check:** Does the plan explicitly mention the **RBAC** (e.g., `RoleGuard`) and **RLS** logic required for this endpoint?
3.  **Traceability:** Does the Step's `Traceability` header link back to the specific section in `docs/05`?
**Fail Condition:** Any endpoint defined in `docs/05` is missing from the "Backend" section of a plan step.

#### **Step 3: Experience Audit (The UI Check)**
**Instruction:** Extract every Route path (e.g., `/settings/billing`, `/patients/new`) from `docs/06 - Frontend Views & Routes.md`.
**Verification:**
1.  Search the Plan for the specific Step where this Route and its Page Component are built.
2.  **Component Check:** Does the step reference the specific components needed (from `docs/07`)?
3.  **State Check:** Does the step reference the specific Query Hooks/Zustand Stores (from `docs/08`) needed to power this page?
4.  **Traceability:** Does the Step's `Traceability` header link back to the route definition in `docs/06`?
**Fail Condition:** Any route in `docs/06` is not explicitly assigned to a implementation step.

---

### **Output: The Implementation Coverage Report**

Produces a report using the following markdown structure. **Do not be vague.** Point to specific line numbers and sections.

```markdown
# Implementation Plan Coverage Report

## 1. Executive Summary
*   **Overall Status:** [PASS / FAIL]
*   **Drift Detected:** [Yes/No] - (Is there anything in the schema/API not in the plan?)

## 2. Missing Scope (Critical Blockers)
*This section lists features present in the Sources of Truth but ABSENT from the Plan.*

| Missing Item | Source Document | Type | Impact |
| :--- | :--- | :--- | :--- |
| `support_tickets` table | `docs/04` | Database | **Critical**: Cannot build Support feature. |
| `GET /api/audit-logs` | `docs/05` | API | **High**: Admin features incomplete. |
| `/settings/security` | `docs/06` | Route | **Medium**: User cannot change password. |

## 3. Traceability Failures
*This section matches steps in the plan that fail to link back to their sources.*

*   **Step [X.Y]:** Missing link to `docs/05` (API Reference).
*   **Step [X.Y]:** References generic "User Table" instead of specific `users` table in `docs/04`.

## 4. Logical & Dependency Errors
*   *Example:* "Step 3 builds the `PatientList` UI but the `GET /api/patients` endpoint isn't built until Step 4."
*   *Example:* "Step 2 requires `S3_BUCKET_NAME` env var, but it is not listed in the Config section."

## 5. Remediation Plan
*Provide exact instructions to fix the plan.*

**Example:**
> **Insert Step 3.5: Support System foundation**
> *   **Traceability:** `docs/04` (lines 200-220), `docs/05` (Support Section)
> *   **Database:** Create `support_tickets`
> *   **API:** Implement `POST /api/tickets`
> *   **UI:** Create `/help` route
```

**Instruction to Reviewer:** If the plan is perfect, explicitly state "100% Coverage Achieved across all 4 domains (DB, API, UI, State)." If not, be ruthless in listing the gaps.