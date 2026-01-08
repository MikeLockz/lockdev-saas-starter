# ADR 001: Frontend API Type Generation and Barrel Exports

**Date**: 2026-01-07  
**Status**: Accepted  
**Decision**: Auto-generate frontend TypeScript types from backend OpenAPI spec with clean barrel file re-exports

## Context

The codebase uses `openapi-typescript` to generate TypeScript types from the FastAPI backend's OpenAPI schema. However, the generated types use a deeply nested structure:

```typescript
import type { components } from '@/lib/api-types';
type User = components['schemas']['UserRead'];
```

This verbose syntax leads to:
1. Developers manually defining duplicate interfaces instead of using generated types
2. Inconsistent type usage across the codebase
3. API contract drift when backend changes aren't reflected in frontend

## Decision

### 1. Create a Barrel File (`models.ts`)

Auto-generate a barrel file that re-exports all schemas with clean, developer-friendly names:

```typescript
// Instead of: components['schemas']['UserRead']
import { User, Organization, Member } from '@/lib/models';
```

**Name mappings** simplify common patterns:
- `UserRead` → `User`
- `OrganizationRead` → `Organization`  
- `SessionListResponse` → `SessionList`

### 2. Automate with Post-Commit Hook

A Git post-commit hook automatically regenerates types when backend API files change:

**Trigger paths:**
- `apps/backend/src/api/*`
- `apps/backend/src/schemas/*`

**Pipeline:**
```
Backend commit → Hook detects API change → generate:schema → generate:types → generate:models → Auto-commit
```

## Consequences

### Positive

| Benefit | Impact |
|---------|--------|
| **Type adoption** | Developers use clean imports instead of writing duplicates |
| **Single source of truth** | Pydantic → OpenAPI → TypeScript pipeline ensures consistency |
| **Compile-time safety** | API breaking changes caught at build, not runtime |
| **Zero manual steps** | Hook automates regeneration on API changes |
| **Self-documenting** | `import { User }` is clearer than nested components path |

### Negative

| Trade-off | Mitigation |
|-----------|------------|
| Hook adds ~5s to commits touching API | Only triggers on API file changes |
| Auto-commit may surprise developers | Clear commit message: "chore: regenerate frontend types" |
| Categories in models.ts are manual | New schemas go to "Other" section automatically |

### Neutral

- Barrel file is generated, not hand-written (reduces maintenance)
- 110 schemas available; 31 categorized with friendly names, 79 in "Other"

## Implementation

### Files Created

| File | Purpose |
|------|---------|
| `apps/frontend/scripts/generate-models.cjs` | Parses `api-types.d.ts`, generates `models.ts` |
| `apps/frontend/src/lib/models.ts` | Clean type exports (auto-generated) |
| `scripts/hooks/post-commit` | Git hook for auto-regeneration |

### Commands

```bash
# Manual regeneration
pnpm generate:types    # OpenAPI → api-types.d.ts
pnpm generate:models   # api-types.d.ts → models.ts

# Hook installation (for new clones)
cp scripts/hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| **Pre-commit hook** | Adds delay to every commit, even non-API changes |
| **CI-only validation** | Types could drift locally during development |
| **Manual regeneration** | Human error; developers forget to regenerate |
| **Direct openapi-typescript output** | Verbose syntax discourages adoption |

## References

- [openapi-typescript](https://openapi-ts.pages.dev/) - Type generation from OpenAPI
- `apps/frontend/src/lib/api-types.d.ts` - Raw generated types
- `apps/frontend/src/lib/models.ts` - Clean barrel exports
