# P0 Remediation Plan

## Overview
This plan addresses 7 critical (P0) issues discovered during the documentation vs implementation review. Each item includes explicit implementation steps and test criteria.

---

## P0-1: Frontend Route Authorization (SECURITY)

> [!CAUTION]
> Patient users can view admin UI by navigating directly to `/admin/*` or `/super-admin/*` routes.

### Problem
Frontend renders admin pages for unauthorized users. The API correctly blocks data, but the UI layout is fully visible.

### Implementation

#### [NEW] [RoleGuard.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/components/auth/RoleGuard.tsx)

```tsx
interface RoleGuardProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode; // Defaults to redirect to /dashboard
}

export function RoleGuard({ allowedRoles, children, fallback }: RoleGuardProps) {
  const { user, membership } = useAuth();
  
  if (!membership || !allowedRoles.includes(membership.role)) {
    return fallback ?? <Navigate to="/403" />;
  }
  
  return <>{children}</>;
}
```

#### [NEW] [403.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/403.tsx)

Create access denied page with:
- "Access Denied" heading
- Message: "You don't have permission to view this page"
- "Return to Dashboard" button

#### [MODIFY] Admin route files
Wrap admin page content in `<RoleGuard allowedRoles={['ADMIN', 'SUPER_ADMIN']}>`:
- `/routes/admin/members.tsx`
- `/routes/admin/staff.tsx`
- `/routes/admin/providers.tsx`
- `/routes/super-admin/*.tsx`

### Test Criteria

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Patient blocked from admin** | 1. Dev login as Patient<br>2. Navigate to `/admin/members` | Redirected to `/403` page |
| **Patient blocked from super-admin** | 1. Dev login as Patient<br>2. Navigate to `/super-admin` | Redirected to `/403` page |
| **Super Admin can access** | 1. Dev login as Super Admin<br>2. Navigate to `/super-admin` | Page loads with data |

---

## P0-2: Signup Page (404)

### Problem
`/signup` returns 404 - route does not exist.

### Implementation

#### [NEW] [signup.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/signup.tsx)

Create signup page with:
- Email input (required)
- Password input (min 8 chars)
- Confirm password input
- "Create Account" button
- Link: "Already have an account? Sign in" → `/login`
- Call `signUpWithEmail(email, password)` from `useAuth()`

### Test Criteria

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Page loads** | Navigate to `/signup` | Form displays without 404 |
| **Form validation** | Submit empty form | Validation errors shown |
| **Link to login** | Click "Sign in" link | Navigates to `/login` |

---

## P0-3: Forgot Password Page (404)

### Problem
`/forgot-password` returns 404 - route does not exist.

### Implementation

#### [NEW] [forgot-password.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/forgot-password.tsx)

Create forgot password page with:
- Email input (required)
- "Send Reset Link" button
- Success message: "If an account exists, you'll receive a reset email"
- Link: "Back to Login" → `/login`
- Call `sendPasswordResetEmail(email)` from Firebase auth

### Test Criteria

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Page loads** | Navigate to `/forgot-password` | Form displays without 404 |
| **Submit email** | Enter email, click submit | Success message shown |
| **Link to login** | Click "Back to Login" | Navigates to `/login` |

---

## P0-4: Login Missing "Forgot Password" Link

### Problem
Login page has no link to password reset flow.

### Implementation

#### [MODIFY] [login.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/login.tsx)

Add below password field:
```tsx
<Link to="/forgot-password" className="text-sm text-primary hover:underline">
  Forgot password?
</Link>
```

### Test Criteria

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Link visible** | Navigate to `/login` | "Forgot password?" link visible below password field |
| **Link works** | Click link | Navigates to `/forgot-password` |

---

## P0-5: Login Missing "Create Account" Link

### Problem
Login page has no link to signup flow.

### Implementation

#### [MODIFY] [login.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/login.tsx)

Add at bottom of card:
```tsx
<p className="text-center text-sm text-muted-foreground">
  Don't have an account?{' '}
  <Link to="/signup" className="text-primary hover:underline">
    Create account
  </Link>
</p>
```

### Test Criteria

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Link visible** | Navigate to `/login` | "Create account" link visible at bottom |
| **Link works** | Click link | Navigates to `/signup` |

---

## P0-6: Patient Messages Tab Non-Functional

### Problem
Messages tab on patient detail page is visible but not clickable/interactive.

### Implementation

#### [MODIFY] Patient detail component

1. Locate patient detail tabs component (likely in `/routes/patients/$patientId/`)
2. Verify Messages tab has proper `onClick` or is a `TabsTrigger` component
3. Ensure corresponding `TabsContent` exists with message list content

### Test Criteria

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Tab clickable** | 1. Navigate to `/patients/{id}`<br>2. Click "Messages" tab | Tab becomes active, content area updates |
| **Content loads** | Same as above | Message list or "No messages" placeholder shown |

---

## P0-7: Notification Bell Missing

### Problem
No notification bell icon in header. Users cannot access quick notifications without navigating to `/notifications`.

### Implementation

#### [NEW] [NotificationBell.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/components/notifications/NotificationBell.tsx)

Create component with:
- Bell icon (from lucide-react)
- Unread count badge (red dot or number)
- Click opens slide-out panel
- Panel shows last 5 notifications
- "View all" link → `/notifications`

#### [MODIFY] Header/AppLayout component

Add `<NotificationBell />` to header, next to user menu.

### Test Criteria

| Test | Steps | Expected Result |
|------|-------|-----------------|
| **Bell visible** | Login and view dashboard | Bell icon visible in header |
| **Panel opens** | Click bell icon | Slide-out panel appears with notifications |
| **View all link** | Click "View all" in panel | Navigates to `/notifications` |

---

## Priority Order

| Priority | Issue | Effort | Dependencies |
|----------|-------|--------|--------------|
| 1 | P0-1: Route Authorization | Medium | New component + modify routes |
| 2 | P0-4: Forgot Password Link | Low | Just add link |
| 3 | P0-5: Create Account Link | Low | Just add link |
| 4 | P0-3: Forgot Password Page | Medium | New route + Firebase integration |
| 5 | P0-2: Signup Page | Medium | New route + Firebase integration |
| 6 | P0-6: Messages Tab | Low | Debug/fix existing component |
| 7 | P0-7: Notification Bell | High | New component + state management |

## Verification Commands

```bash
# Run frontend tests (if they exist)
cd frontend && pnpm test

# Start dev server for manual testing  
make dev

# Open browser to test routes
open http://localhost:5173/login
open http://localhost:5173/signup
open http://localhost:5173/forgot-password
```
