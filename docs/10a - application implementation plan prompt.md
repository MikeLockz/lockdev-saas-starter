You are an expert Senior Software Architect and Technical Lead. Your task is to generate a **complete, exhaustive, and specification-level Implementation Plan** for the "LockDev SaaS Starter".

**CRITICAL INSTRUCTION:** You must ensure **Zero Drift** between the documentation and this plan. Every database table, every API endpoint, and every frontend route defined in the provided documentation **MUST** be accounted for in this plan.

### **Input Documentation (The Truth)**
Analyze these files deeply. They are the strict requirements.
- `docs/00 - Overview.md` (Principles & Goals)
- `docs/03 - implementation.md` (Tech Stack: FastAPI, React, TanStack Query, Zustand, Shadcn)
- `docs/04 - sql.ddl` (Schema: **Strictly adhere to column names/types/constraints**)
- `docs/05 - API Reference.md` (Endpoints: **Strictly adhere to paths, methods, RBAC**)
- `docs/06 - Frontend Views & Routes.md` (UI: **Strictly adhere to route paths and access levels**)
- `docs/09 - backend details.md` (Implementation specifics)

---

### **Execution Strategy**
1.  **Vertical Slices:** Build features end-to-end (DB -> API -> UI). Do not silo "Backend" and "Frontend" work.
2.  **Incremental Completeness:** When building the "Patients" feature, you must implement the *List*, *Create*, *Detail*, *Update*, and *Delete* functionality within that phase. Do not leave "Update" for later.
3.  **Just-in-Time Infrastructure:** Introduce environment variables (`.env`), S3 buckets, or Stripe keys only in the step where they are first used.

---

### **Required Output Format**
The output must be a Markdown document titled `# Detailed Application Implementation Plan`.

**Structure:**
- **Phase X: [Theme]**
    - **Step X.Y: [Feature Set]**

**Template for Every Step (Strictly Follow This):**

```markdown
### Step X.Y: [Feature Name] (e.g., Patient Registration)
**Traceability:**
*   **DDL:** `patients` table, `contact_methods` table.
*   **API:** `POST /api/orgs/{id}/patients`, `GET /api/orgs/{id}/patients`.
*   **UI:** `/patients`, `/patients/new`.

**1. Configuration & Infra**
*   [List required `.env` variables]
*   [List required Cloud Resources e.g., "Create S3 Bucket: lockdev-docs"]

**2. Database (Migrations & Seeding)**
*   **Migration:** Create table `patients` with columns: `id`, `first_name`, `dob`, `...` (Reference `sql.ddl` lines 100-120).
*   **Constraints:** [Explicitly list FKs, Indexes, Unique constraints].
*   **Seeding:** Create script `scripts/seed_patients.py` to insert 5 dummy records for local dev.

**3. Backend (API Layer)**
*   **Models:** Create Pydantic schemas: `PatientCreate`, `PatientResponse`, `PatientUpdate`.
*   **Endpoints:**
    *   `POST /api/...`: Implement logic [Validation -> DB Insert -> Audit Log].
    *   `GET /api/...`: Implement logic [Filtering -> Pagination -> Pydantic Serialize].
*   **Security:**
    *   **RBAC:** Enforce `dependency=get_current_staff`.
    *   **RLS:** Enforce `WHERE organization_id = :current_org_id`.

**4. Frontend (UI Layer)**
*   **State:** Create `usePatients` hook (TanStack Query) with keys `['patients', orgId]`.
*   **Components:**
    *   `PatientTable.tsx`: Uses `DataTable`, handles **Loading Skeleton** and **Empty State**.
    *   `PatientForm.tsx`: Uses `react-hook-form` + `zod`, handles **Validation Errors** and **Submitting State**.
*   **Routes:** Implement `/patients` and `/patients/new` wrapped in `RoleGuard`.

**5. Verification & Testing**
*   **Automated:** Run `pytest tests/api/test_patients.py` and `vitest PatientForm.test.tsx`.
*   **Manual:** Login as Staff, create patient "John Doe", verify redirect to list, verify row in Postgres.
```

---

### **Roadmap Phases**

**Phase 1: Foundation & Identity (The Walking Skeleton)**
*   **Goal:** A deployable app where users can login, switch organizations, and see a dashboard.
*   **Scope:** Project Config, Auth (Firebase), User Table, Org Table, Org Membership, App Shell (Sidebar/Nav), User Profile.
*   **Note:** Include basic Audit Middleware (logging to DB) here, even if the Viewer UI is later.

**Phase 2: Patient Domain (The Core)**
*   **Goal:** Full CRM capability for Patients.
*   **Scope:** Patient Schema, Contact Methods (Safe Contact Logic), Patient List (Search/Filter), Patient Detail View, Patient Edit/Settings.

**Phase 3: Clinical Operations**
*   **Goal:** Provider workflows and Scheduling.
*   **Scope:** Provider/Staff Tables, Care Team Assignments, Appointment Schema, Scheduling UI (Calendar/Form), Appointment Lists.

**Phase 4: Communication & Documents**
*   **Goal:** Secure interaction and file handling.
*   **Scope:** Message Threads/Participants, Secure Messaging UI, Document Table, S3 Integration, File Upload/List UI.

**Phase 5: Access Delegation (Proxies)**
*   **Goal:** Dependent/Guardian access.
*   **Scope:** Proxy Table, Permission Mask Logic, Proxy Invite Flow, Proxy Dashboard View.

**Phase 6: Critical Business Ops**
*   **Goal:** Essential business functions.
*   **Scope:** Call Center Dashboard (Basic), Billing (Stripe) Integration, Super Admin Views (Basic).

**Phase 7: Post-MVP & Enterprise Features**
*   **Goal:** Advanced compliance and tooling.
*   **Scope:** 
    *   **Audit Log Viewer UI:** (Note: Logging happens in Phase 1, viewing is here).
    *   **Break Glass Impersonation:** (Advanced emergency access).
    *   **Advanced Analytics/Telemetry.**

---

### **Final Checklist**
After generating the plan, you (the LLM) must self-correct:
1.  Did I include the **Audit Middleware** setup in Phase 1?
2.  Did I include **Soft Delete** logic in every `DELETE` endpoint?
3.  Did I include **RBAC** checks for every single route?
4.  Did I include **TanStack Query** invalidation logic (e.g., "Invalidate `['patients']` after mutation")?

**Output the full plan now.**