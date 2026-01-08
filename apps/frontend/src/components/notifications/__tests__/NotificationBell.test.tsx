import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
  useUnreadCount,
} from "@/hooks/api/useNotifications";
import { NotificationBell } from "../NotificationBell";

// Mock hooks
vi.mock("@/hooks/api/useNotifications");

// Mock Link
vi.mock("@tanstack/react-router", () => ({
  Link: ({ children, to }: { children: ReactNode; to: string }) => (
    <a href={to}>{children}</a>
  ),
}));

// Mock ResizeObserver for Radix UI (Dropdown)
// Mock ResizeObserver for Radix UI (Dropdown)
vi.stubGlobal(
  "ResizeObserver",
  class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  },
);

// Mock ScrollIntoView (shadcn/ui or browser dependent)
window.HTMLElement.prototype.scrollIntoView = vi.fn();

// Mock pointer capture for Radix
window.HTMLElement.prototype.setPointerCapture = vi.fn();
window.HTMLElement.prototype.releasePointerCapture = vi.fn();
window.HTMLElement.prototype.hasPointerCapture = vi.fn();

describe("NotificationBell", () => {
  const mockMarkRead = vi.fn();
  const mockMarkAllRead = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(useUnreadCount).mockReturnValue({
      data: { count: 3 },
    } as unknown as ReturnType<typeof useUnreadCount>);

    vi.mocked(useNotifications).mockReturnValue({
      data: {
        items: [
          {
            id: "1",
            type: "SYSTEM",
            title: "Test Notification",
            body: "This is a test",
            is_read: false,
            created_at: new Date().toISOString(),
          },
        ],
      },
    } as unknown as ReturnType<typeof useNotifications>);

    vi.mocked(useMarkNotificationRead).mockReturnValue({
      mutate: mockMarkRead,
    } as unknown as ReturnType<typeof useMarkNotificationRead>);

    vi.mocked(useMarkAllNotificationsRead).mockReturnValue({
      mutate: mockMarkAllRead,
    } as unknown as ReturnType<typeof useMarkAllNotificationsRead>);
  });

  it("renders with badge count", () => {
    render(<NotificationBell />);

    // Check badge
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("opens dropdown and shows notifications", async () => {
    const user = userEvent.setup();
    render(<NotificationBell />);

    const trigger = screen.getByRole("button");
    await user.click(trigger);

    expect(await screen.findByText("Test Notification")).toBeInTheDocument();
    expect(screen.getByText("This is a test")).toBeInTheDocument();
  });

  it("calls mark all read when button clicked", async () => {
    const user = userEvent.setup();
    render(<NotificationBell />);

    const trigger = screen.getByRole("button");
    await user.click(trigger);

    const markAllBtn = await screen.findByText("Mark all read");
    await user.click(markAllBtn);

    expect(mockMarkAllRead).toHaveBeenCalled();
  });
});
