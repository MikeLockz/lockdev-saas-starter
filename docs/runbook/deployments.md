# Deployment and Rollback Runbook

## Deployment Process
Deployments are handled via Git push to Aptible.

1. Ensure all tests pass: `make check`.
2. Push to main: `git push origin main`.
3. Push to Aptible: `git push aptible main`.
4. Monitor logs: `aptible logs --app lockdev-api`.

## Rollback Procedure
If a deployment causes issues:

### 1. Revert Git Commit
```bash
git revert HEAD
git push origin main
git push aptible main
```

### 2. Aptible Deploy Previous (If supported by CLI)
If you need an immediate rollback without waiting for a build:
```bash
aptible deploy --app lockdev-api --release [PREVIOUS_RELEASE_ID]
```

## Database Migrations Rollback
If a migration fails or causes issues:

1. Identify the previous migration ID.
2. Run downgrade:
```bash
cd backend
uv run alembic downgrade -1
```
*Note: Always verify if the downgrade script is safe and tested.*
