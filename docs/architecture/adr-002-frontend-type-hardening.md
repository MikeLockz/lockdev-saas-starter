# ADR 002: Frontend Type Hardening

**Date**: 2026-01-07
**Status**: Accepted
**Decision**: Enforce strict type safety, ban `any`, and align forms with API schemas.

## Context

The frontend codebase suffered from:
1.  **Loose Typing**: Explicit use of `any` in hooks and components to bypass type checks.
2.  **Schema Drift**: Manual Zod schemas in forms duplicated logic from the backend and often drifted from the actual API contract.
3.  **Inconsistent Errors**: Error handling logic was fragmented, often swallowing errors or displaying generic messages.

## Decision

### 1. Ban `any` Type
We enforced a strict "no-any" policy to maximize type safety and maintainability.

- **Mechanism**:
    - **Script**: `scripts/check-any.sh` scans source code (excluding tests/generated files).
    - **CI/CD**: `make type-check` fails if `any` is detected.
    - **Pre-commit**: A local hook blocks commits containing explicit `any` types in `apps/frontend`.

### 2. Schema-First Forms
All form validations must start from the generated API schemas.

- **Pattern**:
    ```typescript
    import { ProviderCreate } from "@/lib/api-schemas";

    // Extend generated schema with UI-specific validation
    const formSchema = ProviderCreate.extend({
      // Add UI-only fields or refine rules
      confirmPassword: z.string(),
    });
    ```
- **Benefit**: Ensures form outputs always match the API expectation.

### 3. Typed Error Handling
Standardize error handling using a shared utility that safely parses `AxiosError`.

- **Utility**: `getErrorMessage(error: unknown)`
- **Behavior**: Extracts structured validation errors (`detail`) from 422 responses or falls back to status text.

## Consequences

### Positive
| Benefit | Impact |
|---------|--------|
| **Runtime Safety** | Reduced risk of `undefined is not a function` at runtime. |
| **Refactoring Confidence** | Compiler catches breaking changes immediately. |
| **API Alignment** | Frontend forms automatically stay seeking with backend changes (via generated types). |

### Negative
| Trade-off | Mitigation |
|-----------|------------|
| **Mocking Complexity** | Tests require fully typed mocks instead of `{} as any`. | Use `vi.mocked()` and proper type casting. |
| **Initial Velocity** | writing "quick" prototypes is harder without `any`. | Encourages thoughtful design; use `unknown` if truly necessary. |

## References
- `scripts/check-any.sh`
- `lib/api-error.ts`
- `Makefile` (type-check target)
