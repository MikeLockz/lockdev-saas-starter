# Messaging & Notifications Testing Specification

This document outlines the missing tests needed to achieve high confidence that the messaging and notifications features are fully functional.

## Current State

| Layer | Messaging | Notifications |
|-------|-----------|---------------|
| Backend API (pytest) | ✅ 4 tests | ✅ 6 tests |
| Frontend Unit | ❌ Missing | ❌ Missing |
| E2E (Playwright) | ❌ Missing | ❌ Missing |

---

## Phase 1: Frontend Component Tests

### 1.1 Messaging Components

Create `apps/frontend/src/components/messages/__tests__/`

#### ThreadList.test.tsx

```typescript
import { render, screen } from "@testing-library/react";
import { ThreadList } from "../ThreadList";

const mockThreads = [
  {
    id: "1",
    subject: "Test Thread",
    unread_count: 2,
    last_message: { body: "Hello", sender_name: "Alice" },
    participants: [{ user_name: "Alice" }, { user_name: "Bob" }],
  },
];

describe("ThreadList", () => {
  it("renders empty state when no threads", () => {
    render(<ThreadList threads={[]} onSelect={vi.fn()} selectedId={null} />);
    expect(screen.getByText(/no messages/i)).toBeInTheDocument();
  });

  it("renders thread list with unread indicators", () => {
    render(<ThreadList threads={mockThreads} onSelect={vi.fn()} selectedId={null} />);
    expect(screen.getByText("Test Thread")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument(); // unread badge
  });

  it("calls onSelect when thread clicked", async () => {
    const onSelect = vi.fn();
    render(<ThreadList threads={mockThreads} onSelect={onSelect} selectedId={null} />);
    await userEvent.click(screen.getByText("Test Thread"));
    expect(onSelect).toHaveBeenCalledWith("1");
  });

  it("highlights selected thread", () => {
    render(<ThreadList threads={mockThreads} onSelect={vi.fn()} selectedId="1" />);
    // Assert selected styling applied
  });
});
```

#### ChatInterface.test.tsx

```typescript
describe("ChatInterface", () => {
  it("renders messages in chronological order", () => {});
  it("shows sender name for each message", () => {});
  it("auto-scrolls to latest message on load", () => {});
  it("submits new message on form submit", () => {});
  it("clears input after successful send", () => {});
  it("shows loading state while sending", () => {});
  it("displays error toast on send failure", () => {});
});
```

#### ComposeModal.test.tsx

```typescript
describe("ComposeModal", () => {
  it("renders participant search input", () => {});
  it("allows selecting multiple participants", () => {});
  it("requires subject and message body", () => {});
  it("submits thread creation on confirm", () => {});
  it("closes modal on success", () => {});
  it("shows validation errors for empty fields", () => {});
});
```

### 1.2 Notification Components

Create `apps/frontend/src/components/notifications/__tests__/`

#### NotificationBell.test.tsx

```typescript
describe("NotificationBell", () => {
  it("shows count badge when unread > 0", () => {});
  it("hides badge when unread = 0", () => {});
  it("opens dropdown on click", () => {});
  it("renders recent notifications in dropdown", () => {});
  it("navigates to /notifications on 'View All' click", () => {});
});
```

#### NotificationList.test.tsx

```typescript
describe("NotificationList", () => {
  it("renders notifications grouped by date", () => {});
  it("shows correct icon per notification type", () => {});
  it("toggles read/unread on click", () => {});
  it("supports mark all as read", () => {});
  it("handles empty state gracefully", () => {});
});
```

---

## Phase 2: Hook Integration Tests

### 2.1 useMessaging Hook Tests

Create `apps/frontend/src/hooks/api/__tests__/useMessaging.test.tsx`

```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { useThreads, useCreateThread, useSendMessage } from "../useMessaging";

describe("useMessaging hooks", () => {
  describe("useThreads", () => {
    it("fetches paginated threads", async () => {
      const { result } = renderHook(() => useThreads(1, 20), { wrapper });
      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(result.current.data?.items).toBeDefined();
    });
  });

  describe("useCreateThread", () => {
    it("creates thread and invalidates cache", async () => {});
  });

  describe("useSendMessage", () => {
    it("adds message to existing thread", async () => {});
    it("invalidates thread query on success", async () => {});
  });
});
```

### 2.2 useNotifications Hook Tests

```typescript
describe("useNotifications hooks", () => {
  it("fetches notifications with unread count", async () => {});
  it("marks single notification as read", async () => {});
  it("marks all notifications as read", async () => {});
  it("deletes notification", async () => {});
});
```

---

## Phase 3: E2E Tests (Playwright)

### 3.1 Messaging E2E

Create `apps/frontend/e2e/messaging.spec.ts`

```typescript
import { test, expect } from "@playwright/test";

test.describe("Messaging", () => {
  test.beforeEach(async ({ page }) => {
    // Login as test user
    await page.goto("/login");
    await page.fill('[name="email"]', "alice@test.com");
    await page.fill('[name="password"]', "password123");
    await page.click('button[type="submit"]');
    await page.waitForURL("/dashboard");
  });

  test("can view messages inbox", async ({ page }) => {
    await page.goto("/messages");
    await expect(page.getByRole("heading", { name: "Messages" })).toBeVisible();
  });

  test("can create new thread", async ({ page }) => {
    await page.goto("/messages");
    await page.click('button:has-text("Compose")');
    
    // Fill compose modal
    await page.fill('[placeholder*="Search"]', "bob@test.com");
    await page.click('text=Bob User');
    await page.fill('[name="subject"]', "E2E Test Thread");
    await page.fill('[name="message"]', "Hello from Playwright!");
    await page.click('button:has-text("Send")');
    
    // Verify thread appears
    await expect(page.getByText("E2E Test Thread")).toBeVisible();
  });

  test("can send and receive messages in thread", async ({ page, browser }) => {
    // User A sends message
    await page.goto("/messages");
    await page.click('text=E2E Test Thread');
    await page.fill('[placeholder*="Type a message"]', "Follow-up message");
    await page.click('button[aria-label="Send"]');
    
    await expect(page.getByText("Follow-up message")).toBeVisible();
    
    // User B sees message (new browser context)
    const context2 = await browser.newContext();
    const page2 = await context2.newPage();
    await loginAs(page2, "bob@test.com");
    await page2.goto("/messages");
    await page2.click('text=E2E Test Thread');
    await expect(page2.getByText("Follow-up message")).toBeVisible();
    await context2.close();
  });

  test("thread shows unread count", async ({ page }) => {
    // Assumes thread has unread messages
    await page.goto("/messages");
    const badge = page.locator('[data-testid="unread-badge"]');
    await expect(badge).toBeVisible();
  });
});
```

### 3.2 Notifications E2E

Create `apps/frontend/e2e/notifications.spec.ts`

```typescript
import { test, expect } from "@playwright/test";

test.describe("Notifications", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsTestUser(page);
  });

  test("notification bell shows unread count", async ({ page }) => {
    await page.goto("/dashboard");
    const bell = page.locator('[data-testid="notification-bell"]');
    await expect(bell).toBeVisible();
    // If there are unread notifications, badge should show
  });

  test("can view all notifications", async ({ page }) => {
    await page.goto("/notifications");
    await expect(page.getByRole("heading", { name: "Notifications" })).toBeVisible();
  });

  test("can mark notification as read", async ({ page }) => {
    await page.goto("/notifications");
    const firstNotification = page.locator('[data-testid="notification-item"]').first();
    await firstNotification.click();
    // Verify visual change (read styling)
  });

  test("can mark all as read", async ({ page }) => {
    await page.goto("/notifications");
    await page.click('button:has-text("Mark all as read")');
    // Verify all items show read state
    await expect(page.locator('[data-unread="true"]')).toHaveCount(0);
  });

  test("notification triggers when message received", async ({ page, browser }) => {
    // User B sends message to User A
    const context2 = await browser.newContext();
    const page2 = await context2.newPage();
    await loginAs(page2, "bob@test.com");
    await sendMessageTo(page2, "alice@test.com", "Notification test");
    await context2.close();

    // User A sees notification
    await page.reload();
    const bell = page.locator('[data-testid="notification-bell"] [data-testid="badge"]');
    await expect(bell).toContainText(/[1-9]/);
  });
});
```

---

## Phase 4: Backend Integration Tests (Extended)

### 4.1 Missing Backend Test Cases

Add to `apps/backend/tests/api/test_messaging.py`:

```python
@pytest.mark.asyncio
async def test_non_participant_cannot_view_thread(client, test_user_token_headers, test_org, other_user, third_user_headers):
    """Verify 403 when non-participant tries to access thread."""
    # Create thread between user A and B
    resp = await client.post(...)
    thread_id = resp.json()["id"]
    
    # User C tries to access
    response = await client.get(f"/api/v1/users/me/threads/{thread_id}", headers=third_user_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_mark_thread_read_updates_timestamp(client, test_user_token_headers, test_org, other_user):
    """Verify mark_read updates last_read_at."""
    pass

@pytest.mark.asyncio
async def test_unread_count_decrements_after_read(client, ...):
    """Verify unread count reflects read status."""
    pass
```

Add to `apps/backend/tests/api/test_notifications.py`:

```python
@pytest.mark.asyncio
async def test_notification_created_on_new_message(client, ...):
    """Verify notification is sent when user receives new message."""
    pass

@pytest.mark.asyncio
async def test_cannot_access_other_users_notifications(client, ...):
    """Verify 404/403 for cross-user notification access."""
    pass
```

---

## Implementation Checklist

### Frontend Component Tests
- [ ] `ThreadList.test.tsx`
- [ ] `ChatInterface.test.tsx`
- [ ] `ComposeModal.test.tsx`
- [ ] `NotificationBell.test.tsx`
- [ ] `NotificationList.test.tsx`
- [ ] `NotificationItem.test.tsx`

### Frontend Hook Tests
- [ ] `useMessaging.test.tsx`
- [ ] `useNotifications.test.tsx`

### E2E Tests
- [ ] `messaging.spec.ts`
- [ ] `notifications.spec.ts`

### Backend Extended Tests
- [ ] Authorization boundary tests
- [ ] Cross-user isolation tests
- [ ] Notification trigger tests

---

## Verification Commands

```bash
# Run frontend unit tests
pnpm --filter frontend test

# Run frontend tests with coverage
pnpm --filter frontend test -- --coverage

# Run E2E tests
pnpm --filter frontend test:e2e

# Run specific E2E file
pnpm --filter frontend test:e2e -- messaging.spec.ts

# Run backend tests
cd apps/backend && pytest tests/api/test_messaging.py tests/api/test_notifications.py -v

# Run all tests
make test
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Frontend component test coverage | ≥ 80% |
| Hook test coverage | ≥ 90% |
| E2E test pass rate | 100% |
| Backend API test coverage | ≥ 90% |
| Zero flaky tests | Required |
