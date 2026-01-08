#!/bin/bash

# Find explicit 'any' usage, excluding tests and generated files
# We search for ": any" (exact type annotation) and "as any" (type assertion)
# Usage of "any" in comments is ignored if strictly searching for code patterns, but grep text search might catch them.
# We try to be specific.

FOUND=$(grep -rE ": any\b|as any\b" src \
  --include="*.ts" --include="*.tsx" \
  --exclude="api-schemas.ts" \
  --exclude="routeTree.gen.ts" \
  --exclude="*.test.ts" \
  --exclude="*.test.tsx" \
  --exclude="vite-env.d.ts" \
  --exclude="*.d.ts")

if [ -n "$FOUND" ]; then
  echo "Error: Explicit 'any' types found in the following files:"
  echo "$FOUND"
  exit 1
else
  echo "Success: No explicit 'any' types found (excluding tests and generated files)."
  exit 0
fi
