# Story 16.4: Communications Frontend
**User Story:** As a User, I want a UI for notifications and messaging.

## Status
- [x] **Done**

## Context
- **Roadmap Ref:** Step 5.1 from `docs/10 - application implementation plan.md`
- **UI Ref:** `docs/06 - Frontend Views & Routes.md` (Routes: `/notifications`, `/messages`)

## Technical Specification
**Goal:** Implement notification panel and chat interface.

**Changes Required:**

1.  **Routes:** `frontend/src/routes/_auth/`
    - `notifications.tsx` - Full notification list
    - `messages/index.tsx` - Message inbox
    - `messages/$threadId.tsx` - Thread view

2.  **Components:** `frontend/src/components/notifications/`
    - `NotificationBell.tsx`
      - Header icon with unread badge
      - Dropdown preview of recent notifications
    - `NotificationList.tsx`
      - Full list with filters
      - Mark read/unread toggle
      - Mark all read button
    - `NotificationItem.tsx`
      - Type-specific icon and styling
      - Click to navigate to context

3.  **Components:** `frontend/src/components/messages/`
    - `ThreadList.tsx`
      - Inbox with thread previews
      - Unread indicators
    - `ChatInterface.tsx`
      - Message thread view
      - Message input at bottom
      - Auto-scroll to latest
    - `ComposeModal.tsx`
      - New thread creation
      - Participant selection

4.  **Hooks:** `frontend/src/hooks/api/`
    - `useNotifications.ts` - List with unread count
    - `useMarkRead.ts` - Mutations
    - `useThreads.ts` - Message inbox
    - `useThread.ts` - Single thread with messages
    - `useSendMessage.ts` - Mutation

## Acceptance Criteria
- [x] Notification bell shows unread count.
- [x] Dropdown shows recent notifications.
- [x] `/notifications` shows full list.
- [x] `/messages` shows inbox.
- [x] Thread view shows conversation.
- [x] Can compose and send messages.

## Verification Plan
**Automated Tests:**
- `pnpm test -- NotificationBell`
- `pnpm test -- ChatInterface`

**Manual Verification:**
- Receive notification, see in bell.
- Open messages, start conversation.
