
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { NotificationBell } from "../NotificationBell";
import { useNotifications, useUnreadCount, useMarkNotificationRead, useMarkAllNotificationsRead } from "@/hooks/api/useNotifications";
import userEvent from "@testing-library/user-event";

// Mock hooks
vi.mock("@/hooks/api/useNotifications");

// Mock Link
vi.mock("@tanstack/react-router", () => ({
    Link: ({ children, to }: any) => <a href={to}>{children}</a>,
}));

// Mock ResizeObserver for Radix UI (Dropdown)
(globalThis as any).ResizeObserver = class ResizeObserver {
    observe() { }
    unobserve() { }
    disconnect() { }
};

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

        (useUnreadCount as any).mockReturnValue({
            data: { count: 3 },
        });

        (useNotifications as any).mockReturnValue({
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
        });

        (useMarkNotificationRead as any).mockReturnValue({
            mutate: mockMarkRead,
        });

        (useMarkAllNotificationsRead as any).mockReturnValue({
            mutate: mockMarkAllRead,
        });
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
