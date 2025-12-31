# Story 3.7: Mobile PWA Setup
**User Story:** As a Mobile User, I want the app to work on my phone and handle offline states gracefully, so that I can use it on the go.

## Status
- [ ] **Pending**

## Context
- **Roadmap Ref:** Step 3.7 from `docs/03`

## Technical Specification
**Goal:** Configure PWA manifest and Service Worker.

**Changes Required:**
1.  **File:** `frontend/vite.config.ts`
    - Add `VitePWA` plugin.
    - Strategy: **NetworkOnly** for `/api/*`.
    - Cache: App Shell only.
2.  **Manifest:** Define icons, colors.

## Acceptance Criteria
- [ ] App is installable.
- [ ] Offline mode shows "No Internet" but loads app shell.
- [ ] API requests are NOT cached.

## Verification Plan
**Manual Verification:**
- Build app. Serve. Toggle "Offline" in DevTools.
- Verify App Shell loads.
- Verify API call fails (correct behavior).
