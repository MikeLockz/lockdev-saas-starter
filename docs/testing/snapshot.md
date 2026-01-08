# Snapshot Testing Specification

## Overview
Snapshot testing is a useful tool for ensuring that your UI does not change unexpectedly. A snapshot test renders a UI component, takes a "snapshot" of the rendered output, and compares it to a reference snapshot file stored alongside the test. The test will fail if the two snapshots do not match: either the change is unexpected (a regression), or the reference snapshot needs to be updated to the new version of the UI component.

## Tools
We leverage the existing testing infrastructure in `apps/frontend`:

### Unit & Integration (Component Logic)
- **Runner**: [Vitest](https://vitest.dev/) (compatible with Jest).
- **Utils**: [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) for rendering components.
- **Environment**: jsdom.

### E2E & Visual Regression (Pixels)
- **Runner**: [Playwright](https://playwright.dev/).
- **Snapshot Logic**: `expect(page).toHaveScreenshot()` avoids the brittleness of DOM snapshots by comparing rendered pixels.

## Guidelines

### What to Snapshot
- **Atomic Components**: Buttons, Badges, Inputs, and other design system primitives.
- **Critical UI States**: Error states, empty states, and complex layouts where visual structure is critical.
- **Fixed Content**: Static text and structure that rarely changes but is important for compliance or UX.
- **Application State**: Reducers, Zustand stores, or context values can be snapshotted to ensure state transitions produce the expected data structure.
- **API Responses**: Serializable objects/JSON from API transformations or mocked responses.

### What NOT to Snapshot
- **Dynamic Content**: Avoid snapshotting content that changes every run (e.g., timestamps, generated IDs) unless mocked.
- **Implementation Details**: Avoid snapshotting internal instance properties or logic that doesn't affect the rendered output.
- **Large Components**: Avoid snapshotting entire pages or huge containers as they become brittle and hard to review.
- **Large Data Structures**: Avoid large API responses unless you use property matchers to ignore volatile fields.

## Implementation Standard

Use `toMatchSnapshot()` from Vitest's expect API.

### UI Component Example

```tsx
// src/components/ui/__tests__/Button.test.tsx
import { render } from '@testing-library/react';
import { Button } from '../button';

describe('Button', () => {
  it('renders correctly with default props', () => {
    const { asFragment } = render(<Button>Click me</Button>);
    expect(asFragment()).toMatchSnapshot();
  });
});
```

### State Management Example (Zustand/Reducers)

Snapshot testing is excellent for verifying complex state logic without writing assertions for every specific field.

```ts
// src/store/__tests__/cart-store.test.ts
import { createStore } from 'zustand';
import { cartStore } from '../cart-store';

describe('Cart Store', () => {
  it('adds an item to the cart accurately', () => {
    const state = cartStore.getState();
    state.addItem({ id: '123', name: 'Product', price: 100 });
    
    // Snapshots the entire serializable state object
    expect(cartStore.getState()).toMatchSnapshot();
  });
});
```

## Workflow

1.  **Writing Tests**: Create a test file (e.g., `Button.test.tsx`) and add a snapshot assertion.
2.  **Generating Snapshots**: Run the test. Vitest will create a `__snapshots__` directory containing the snapshot file.
3.  **Reviewing Changes**: When a snapshot test fails, review the diff output.
    -   If the change is **unintentional**, fix the code.
    -   If the change is **intentional**, update the specific snapshot.

## Commands

### Run Tests
```bash
# Run all tests
npm test

# Run specific test file
npm test Button.test.tsx
```

### Update Snapshots
To update snapshots when changes are intentional:

```bash
# Update all snapshots
npm test -- -u


## Implementation Plan

This plan outlines the specific areas to target for snapshot testing, categorized by test type.

### Phase 1: Design System Primitives (Unit / DOM)
**Goal**: Ensure atomic components remain stable and prevent accidental styling regressions.
**Tool**: Vitest + React Testing Library

| Component | Test Scenarios |
| :--- | :--- |
| `components/ui/alert-dialog.tsx` | Open state with title, description, and actions. |
| `components/ui/avatar.tsx` | Image loaded, fallback state. |
| `components/ui/badge.tsx` | Default, Secondary, Destructive, Outline variants. |
| `components/ui/button.tsx` | Default, Destructive, Outline, Ghost variants; Loading state; Icon combinations. |
| `components/ui/card.tsx` | Header, Title, Description, Content, Footer structure. |
| `components/ui/command.tsx` | Input, List, Item, Empty state, Group rendering. |
| `components/ui/dialog.tsx` | Trigger, Content open state, Header/Footer layout. |
| `components/ui/dropdown-menu.tsx` | Trigger, Content open state, Items, Checkbox items, Radio items, Submenus. |
| `components/ui/form.tsx` | Label, Control, Description, Error Message states. |
| `components/ui/input.tsx` | Default, Error state, Disabled state, File type. |
| `components/ui/label.tsx` | Default text style. |
| `components/ui/popover.tsx` | Trigger, Content open state. |
| `components/ui/progress.tsx` | 0%, 50%, 100% value states. |
| `components/ui/scroll-area.tsx` | Vertical and Horizontal scrollbar visibility. |
| `components/ui/select.tsx` | Trigger (placeholder/value), Content open state, Item groups. |
| `components/ui/separator.tsx` | Horizontal and Vertical orientations. |
| `components/ui/sheet.tsx` | Trigger, Content open state (Side: top/bottom/left/right). |
| `components/ui/sidebar.tsx` | Expanded/Collapsed states, Menu items, Grouping. |
| `components/ui/skeleton.tsx` | Default animation and shape. |
| `components/ui/sonner.tsx` | Toast appearance (Success, Error, Info). |
| `components/ui/switch.tsx` | Checked, Unchecked, Disabled states. |
| `components/ui/table.tsx` | Header, Body, Row, Cell, Caption structure. |
| `components/ui/tabs.tsx` | List, Trigger (active/inactive), Content visibility. |
| `components/ui/textarea.tsx` | Default, Disabled, Placeholder states. |
| `components/ui/tooltip.tsx` | Trigger hover state, Content positioning. |

### Phase 2: Core State Logic (Unit / State)
**Goal**: Verify complex state management logic and data transformations.
**Tool**: Vitest

| Store / Logic | Test Scenarios |
| :--- | :--- |
| `store/org-store.ts` | Initial state; State after selecting an organization; State after clearing organization. |
| `store/auth-store.ts` | State validation after login (user profile presence); State after logout. |
| `lib/api-schemas.ts` | Verify Zod schema parsing produces expected shapes for complex mocked responses. |

### Phase 3: Critical User Flows (E2E / Visual)
**Goal**: Catch visual bugs in full-page layouts that unit tests miss (e.g., spacing, z-index, font rendering).
**Tool**: Playwright

#### Public & Onboarding
| Route / Component | Test Scenarios |
| :--- | :--- |
| `routes/login.tsx` | Desktop/Mobile layouts; Error states; MFA prompt. |
| `routes/_auth/consent.tsx` | Document viewer layout; Signature acceptance flow. |
| `routes/_auth/index.tsx` | Onboarding wizard steps (Profile, MFA setup). |

#### Patient & Proxy
| Route / Component | Test Scenarios |
| :--- | :--- |
| `routes/_auth/dashboard.tsx` | Patient view (Appointments, Messages); Proxy view (Managed patients list). |
| `routes/_auth/appointments/index.tsx` | Appointment cards; Past/Upcoming tabs. |
| `routes/_auth/messages/index.tsx` | Inbox layout; Thread list. |
| `routes/_auth/proxy/patients.tsx` | Patient card grid; Permission badges. |

#### Provider & Clinical Staff
| Route / Component | Test Scenarios |
| :--- | :--- |
| `routes/_auth/patients/index.tsx` | Patient list table; Search/Filter states. |
| `routes/_auth/patients/$patientId.tsx` | Patient detail layout (Header, Tabs). |
| `routes/_auth/patients/new.tsx` | Patient registration form. |
| `components/care-team/CareTeamList.tsx` | Provider assignment cards. |

#### Admin & Super Admin
| Route / Component | Test Scenarios |
| :--- | :--- |
| `routes/_auth/admin/staff.tsx` | Staff management table. |
| `routes/_auth/admin/providers.tsx` | Provider list; License expiry warnings. |
| `routes/_auth/admin/billing.tsx` | Billing overview; Subscription status. |
| `routes/_auth/super-admin/index.tsx` | Platform dashboard; Org list. |

## Make Commands

To maintain consistency with the project's tooling, we will add a dedicated Make command for failing on snapshot diffs, and ensure it's part of the main test suite.

### New Command
Add the following to the `Makefile`:
```makefile
test-snapshot:
	@echo "Running Snapshot Tests..."
	cd apps/frontend && pnpm test --run 
```
*Note: Vitest runs snapshot checks by default during standard test runs.*

### Updating Existing `test` Command
Include the snapshot check (which is covered by standard tests) in the main `test` command.

```makefile
test:
	@echo "Running Tests..."
	@echo "Backend..."
	docker compose exec api python -m pytest
	@echo "Frontend (includes snapshots)..."
	cd apps/frontend && pnpm test
```

