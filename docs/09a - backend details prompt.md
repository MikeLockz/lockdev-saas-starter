You are an expert Backend Developer and Software Architect. Your task is to generate a comprehensive **Backend Implementation Specification** for the API endpoints defined in the project.

**Inputs:**
1.  `docs/05 - API Reference.md`: Contains the list of API endpoints, request/response schemas, and high-level behavior.
2.  `docs/04 - sql.ddl`: Contains the database schema, table definitions, and relationships.

**Output:**
-   Generate a new file named `docs/09 - backend details.md`.

**Instructions:**
Iterate through **every** API endpoint listed in the `docs/05 - API Reference.md`. For each endpoint, provide a detailed technical breakdown of how it should be implemented.

**Format for Each Endpoint:**

### `{HTTP_METHOD} {ENDPOINT_PATH}`
**Summary**: A one-sentence description of what this endpoint does.

**1. Function Signature (Python/FastAPI)**
*   Define the suggested function name and signature.
*   List all **Inputs**: Path parameters, Query parameters, Request Body (Pydantic model fields), and Dependency injections (e.g., `current_user`, `db_session`).
*   List **Outputs**: The Pydantic model or response structure.

**2. Business Logic & Control Flow**
*   Step-by-step logical flow of the function.
*   **Authentication/Authorization**: value specific role checks (e.g., "Check if `current_user.role` is 'ADMIN'").
*   **Validation**: Specific checks beyond standard type checking (e.g., "Verify `start_time` is before `end_time`").
*   **Processing**: Any data transformation, calculations, or complex logic.

**3. Database Interactions (SQL/ORM)**
*   Detail the exact queries required.
*   **Reference specific tables and columns** from `docs/04 - sql.ddl`.
*   *Example:* "SELECT * FROM `patients` WHERE `organization_id` = :org_id AND `id` = :patient_id AND `deleted_at` IS NULL".
*   Mention transaction boundaries if multiple updates are needed.

**4. External Service Calls**
*   Identify any interactions with external systems (e.g., Stripe, Firebase Auth, Twilio, SendGrid).
*   Describe what data is sent and what is expected back.

**5. Error Handling**
*   List specific error conditions and the corresponding HTTP Status Codes and Error Codes.
*   *Example:* "If patient not found or `deleted_at` is set -> 404 NOT_FOUND".

---

**General Guidelines:**
*   **Completeness**: Do not skip endpoints. Cover everything from Authentication to Webhooks.
*   **Security**: Explicitly mention RLS (Row Level Security) patterns or tenant isolation checks (e.g., "Ensure `organization_id` in the URL matches the user's membership").
*   **Performance**: Note if any queries need indexing (referencing the DDL) or if pagination strategies are critical.
*   **Conventions**: Assume a standard FastAPI service structure (Controllers -> Services -> Repositories).
