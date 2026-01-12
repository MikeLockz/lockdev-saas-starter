# Project Rules for AI Agents

> These rules guide AI agents when generating code for this HIPAA-compliant SaaS healthcare application.

---

## 1. Project Structure

```
lockdev-saas-starter/
├── apps/
│   ├── backend/      # FastAPI + SQLAlchemy (Python)
│   │   ├── src/      # Application code
│   │   │   └── workers/  # ARQ background job definitions
│   │   ├── tests/    # Pytest tests
│   │   ├── migrations/  # Alembic migrations
│   │   └── scripts/  # Seed and utility scripts
│   ├── frontend/     # Vite + React (TypeScript)
│   │   ├── src/
│   │   │   ├── components/  # React components
│   │   │   ├── hooks/       # Custom React hooks (TanStack Query)
│   │   │   ├── routes/      # TanStack Router pages
│   │   │   ├── store/       # Zustand state stores
│   │   │   └── lib/         # Utilities (axios, firebase, api client)
│   │   └── e2e/      # Playwright E2E tests
│   └── worker/       # (Future) Standalone worker service
├── agent/            # AI Agent workflow (this codebase)
├── docs/             # Project documentation
└── Makefile          # Monorepo commands (ALWAYS use these)
```

### Code Location Guide
| Code Type | Location |
|-----------|----------|
| API routes, services, models | `apps/backend/` |
| React components, hooks, pages | `apps/frontend/` |
| Background jobs (ARQ) | `apps/backend/src/workers/` |
| Shared packages | `packages/` |

---

## 2. Tech Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async support)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Background Jobs**: ARQ (Redis-based)
- **Auth**: Firebase Admin SDK (Google Cloud Identity Platform)
- **Linting**: Ruff
- **Dependency Management**: uv

### Frontend
- **Build Tool**: Vite
- **Framework**: React 18 + TypeScript
- **Routing**: TanStack Router (file-based)
- **Data Fetching**: TanStack Query
- **Forms**: TanStack Form + Zod
- **State**: Zustand
- **Type Safety**: STRICTLY NO `any`. Use generated API types (`src/lib/api-types.d.ts`) or Zod schemas (`src/lib/api-schemas.ts`).
- **UI Components**: shadcn/ui (Radix primitives)
- **HTTP Client**: Axios
- **Linting**: Biome
- **Package Manager**: pnpm

---

## 3. Command Reference

> [!IMPORTANT]
> **Always use Makefile commands.** Never run `npx`, `pnpm`, `uv`, or `docker compose` directly.
> If unsure what command to use, run `make help` for a full list.

```bash
# Development
make dev              # Start full dev environment (Docker + Vite)
make stop             # Stop all dev processes
make dev-logs         # View backend API logs
make dev-logs-worker  # View ARQ worker logs
make dev-logs-all     # View all service logs

# Quality Checks
make check            # Run all linters (Ruff + Biome + pre-commit)
make test             # Run all tests (backend + frontend)
make test-backend     # Backend tests only (pytest)
make test-frontend    # Frontend tests only (vitest)

# Database
make migrate          # Run Alembic migrations
make seed             # Seed E2E test data
make seed-e2e         # Seed E2E users (super admin, staff, provider, patient)
make seed-patients    # Seed 50 dummy patients

# Utilities
make clean            # Remove generated files and caches
make install-all      # Install all dependencies (backend + frontend)
make help             # Show all available commands
```

---

## 4. Database Conventions

### Primary Keys
- **ULID**: All entities use ULID (Universally Unique Lexicographically Sortable Identifier) as primary keys
- Never use sequential integers for IDs

### Soft Deletes
- Always use `deleted_at` timestamp column instead of hard deletes
- Filter out soft-deleted records in queries by default

### Auditing
- All database mutations trigger PostgreSQL audit logs
- Read access logging is enforced for PHI data

### Multi-Tenancy
- Data is isolated by `organization_id`
- Always filter queries by the user's authorized organizations

### Timestamps
- All timestamps stored as UTC with timezone awareness
- Use `created_at` and `updated_at` columns on all entities

---

## 5. API Conventions

### URL Structure
```
/api/v1/organizations/{org_id}/[resource]
/api/v1/users/me
/api/v1/admin/[resource]  # Super Admin only
```

### Authentication
- Firebase JWT tokens in `Authorization: Bearer <token>` header
- All endpoints require authentication except `/health` and `/docs`

### Response Format
- Return Pydantic models directly (FastAPI serializes to JSON)
- Use HTTP status codes correctly (201 for creates, 204 for deletes)

### Pagination
- Use `skip` and `limit` query parameters
- Default limit: 50, max limit: 100

### Error Handling
- Raise `HTTPException` with appropriate status codes
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 422: Unprocessable Entity (Pydantic validation)

---

## 6. Backend Code Patterns

### File Organization
```
apps/backend/src/
├── api/
│   └── v1/
│       ├── endpoints/   # Route handlers
│       └── deps.py      # Dependency injection
├── core/
│   ├── config.py        # Settings (Pydantic Settings)
│   ├── security.py      # Auth utilities
│   └── database.py      # SQLAlchemy engine/session
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
└── workers/             # ARQ background tasks
```

### Import Patterns
```python
# Models
from src.models.user import User
from src.models.organization import Organization

# Schemas
from src.schemas.user import UserCreate, UserRead

# Dependencies
from src.api.v1.deps import get_current_user, get_db
```

### Endpoint Pattern
```python
@router.get("/{id}", response_model=EntityRead)
async def get_entity(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EntityRead:
    entity = await service.get_by_id(db, id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity
```

---

## 7. Frontend Code Patterns

### Hook Naming
- Data fetching: `useEntity`, `useEntities`, `useEntityById`
- Mutations: `useCreateEntity`, `useUpdateEntity`, `useDeleteEntity`
- Query keys: `['entity', id]` or `['entities', { orgId, filters }]`

### Component Organization
```typescript
// Barrel exports in components/index.ts
export { EntityTable } from './EntityTable';
export { EntityForm } from './EntityForm';
export { EntityCard } from './EntityCard';
```

### Import Patterns (use path aliases)
```typescript
// ✅ Correct
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';

// ❌ Wrong
import { useAuth } from '../../../hooks/useAuth';
```

### TanStack Query Pattern
```typescript
export function useEntity(id: string) {
  return useQuery({
    queryKey: ['entity', id],
    queryFn: () => api.get(`/api/v1/entities/${id}`).then(r => r.data),
    enabled: !!id,
  });
}
```

---

## 8. User Roles & Permissions

| Role | Description | Scope |
|------|-------------|-------|
| **Super Admin** | Platform owner | Full access to all tenants |
| **Org Admin** | Organization administrator | Manage org settings and users |
| **Provider** | Licensed clinician (MD, NP, PA) | Clinical access, scheduling |
| **Staff** | Clinical/Administrative staff | Limited clinical access |
| **Patient** | Self-managed patient | Own records only |
| **Proxy** | Patient guardian/caretaker | Delegated patient access |

Always check user permissions before returning data or allowing mutations.

---

## 9. Security & Compliance (HIPAA)

### Data Handling
- Never log PHI (Protected Health Information)
- Use Presidio for PII masking in logs
- All API requests are rate-limited (SlowAPI)

### Audit Requirements
- Every data mutation is logged with actor, action, timestamp
- Read access to PHI is logged for staff users
- Audit logs are immutable (append-only)

### Safe Contact Protocol
- Check `is_safe_for_voicemail` before leaving PHI in messages
- Distinguish between primary and safe contact methods

### Secrets Management
- Never hardcode secrets
- Use environment variables via Pydantic Settings
- Secrets are encrypted with SOPS/Age for version control

---

## 10. Testing Requirements

### Backend Tests (pytest)
- Unit tests for services
- Integration tests for API endpoints
- Use fixtures for database setup/teardown

### Frontend Tests (vitest)
- Unit tests for hooks and utilities
- Component tests with React Testing Library

### E2E Tests (Playwright)
- Located in `apps/frontend/e2e/`
- Test critical user flows (login, patient CRUD, appointments)

### Before Committing
Always run:
```bash
make check  # Linting
make test   # All tests
```

---

## 11. Critical Reminders

1. **No Hard Deletes**: Always use soft delete (`deleted_at`)
2. **Always Filter by Org**: Multi-tenant data must be org-scoped
3. **ULID for IDs**: Never use `int` or `uuid` for primary keys
4. **UTC Timestamps**: Store all times as UTC, display in user's timezone
5. **Path Aliases**: Use `@/` imports, never relative paths like `../../../`
6. **Pydantic v2**: Use model_validate, not parse_obj
7. **Async by Default**: All database operations should be async
8. **Run Checks First**: Before writing new code, run `make check` to understand current state
9. **Use Makefile Commands**: Never run `npx`, `pnpm`, `uv`, or `docker compose` directly—use `make` targets
10. **No Explicit Any**: Strictly avoid `any` types. Use generated types, `unknown`, or `Record<string, unknown>`.
11. **When Unsure**: Run `make help` to see all available commands
