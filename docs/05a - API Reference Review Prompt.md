# API Reference Documentation Review Prompt

You are a Senior API Technical Writer and Backend Architect. Review the API Reference documentation (`docs/05 - API Reference.md`) for completeness, accuracy, and developer experience quality.

## Review Criteria

### 1. Completeness Check
- [ ] **All CRUD operations covered**: Does every resource (Users, Organizations, Patients, Providers, Proxies, etc.) have appropriate GET, POST, PATCH, DELETE endpoints?
- [ ] **Missing endpoints**: Cross-reference with `docs/04 - sql.ddl` tables — is there an endpoint for every table that requires API access?
- [ ] **Request/Response schemas**: Does every endpoint have complete request body and response examples?
- [ ] **Query parameters**: Are pagination (`limit`, `offset`), filtering, and search parameters documented for list endpoints?
- [ ] **Path parameters**: Are all path parameters (`:id`, `:org_id`, etc.) documented with types?

### 2. Consistency Check
- [ ] **Naming conventions**: Are endpoint paths consistent? (e.g., always `/api/organizations/{org_id}/...` for org-scoped resources)
- [ ] **HTTP methods**: Are methods used correctly? (GET for reads, POST for creates, PATCH for partial updates, DELETE for removals)
- [ ] **Response formats**: Do all endpoints follow the same response structure?
- [ ] **Error codes**: Are error responses consistent across endpoints?
- [ ] **ID format**: Are all IDs documented as ULID where applicable?

### 3. Security & Compliance
- [ ] **Authentication requirements**: Is auth requirement clearly stated for each endpoint?
- [ ] **Authorization/roles**: Are role requirements specified? (ADMIN, PROVIDER, STAFF, etc.)
- [ ] **Audit logging notes**: Are endpoints that trigger audit logs clearly marked?
- [ ] **HIPAA considerations**: Are PHI-related endpoints flagged appropriately?
- [ ] **Rate limiting**: Is rate limiting documented?

### 4. Developer Experience
- [ ] **Examples are copy-pasteable**: Can developers copy JSON examples directly into tools like Postman/curl?
- [ ] **Error handling guidance**: Are common error scenarios documented?
- [ ] **Related endpoints linked**: Are related endpoints cross-referenced?
- [ ] **Versioning strategy**: Is API versioning documented (if applicable)?

### 5. Gap Analysis
Cross-reference these sources and identify missing endpoints:
1. `docs/03 - Implementation.md` — Any feature described without a corresponding endpoint?
2. `docs/04 - sql.ddl` — Any table without CRUD endpoints?
3. `docs/06 - Frontend Views & Routes.md` — Any view that requires an API call not documented?

---

## Output Format

Provide your review as:

1. **Summary**: Overall assessment (Complete/Mostly Complete/Incomplete)
2. **Missing Endpoints**: List any endpoints that should exist but don't
3. **Inconsistencies**: List any naming, format, or structural inconsistencies
4. **Improvements**: Specific suggestions to improve documentation quality
5. **Recommended Additions**: New sections or details to add

---

## Files to Reference
- `docs/05 - API Reference.md` (primary document to review)
- `docs/03 - Implementation.md` (source of truth for features)
- `docs/04 - sql.ddl` (database schema)
- `docs/06 - Frontend Views & Routes.md` (consumer requirements)
