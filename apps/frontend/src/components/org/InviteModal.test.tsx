import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useCreateInvitation } from "../../hooks/useCreateInvitation";
import { useCurrentOrg } from "../../hooks/useCurrentOrg";
import { InviteModal } from "./InviteModal";

// Mock hooks
vi.mock("../../hooks/useCreateInvitation");
vi.mock("../../hooks/useCurrentOrg");

// Mock ResizeObserver for Radix UI
(globalThis as any).ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock the dialog to avoid portal/state complexity in simple unit test
// We want to verify form submission logic, not Radix behavior
vi.mock("../ui/dialog", () => ({
  Dialog: ({ children, open }: any) => (
    <div>
      {open ? <div data-testid="dialog-content">{children}</div> : children}
    </div>
  ),
  DialogTrigger: ({ children, onClick }: any) => (
    <button onClick={onClick} data-testid="dialog-trigger">
      {children}
    </button>
  ),
  DialogContent: ({ children }: any) => <div>{children}</div>,
  DialogHeader: ({ children }: any) => <div>{children}</div>,
  DialogTitle: ({ children }: any) => <div>{children}</div>,
  DialogDescription: ({ children }: any) => <div>{children}</div>,
  DialogFooter: ({ children }: any) => <div>{children}</div>,
}));

// We need to simulate the state change since we mocked the Dialog which usually handles it.
// Actually, since InviteModal controls the state `const [open, setOpen] = useState(false)`,
// and passes it to Dialog.
// But the trigger in InviteModal is:
// <DialogTrigger asChild> <Button>Invite Member</Button> </DialogTrigger>
// Use `asChild` means the Button gets the onClick.
// But Radix's DialogTrigger injects the onClick.
// Since we mocked DialogTrigger, we lost the injection.
// So we can't easily test opening it with a shallow mock unless we manually expose the setOpen or verify the hook call directly.

// ALTERNATIVE: Mock the whole component? No, we want to test IT.
// Let's use REAL internal logic but simulated trigger.
// If I change the mock:
// DialogTrigger just renders children.
// The Button inside has an onClick? No, Radix adds it.
//
// Let's try to test ONLY that it renders the button, and if we force the modal open (by finding the button and clicking it - wait, the click handler is missing),
// we might be blocked.
//
// BETTER STRATEGY for this specific generic component test:
// Just verify the hook is called when we submit the form.
// But we need to see the form.
//
// Let's modify the component slightly to be more testable? No.
// Let's use the REAL Dialog and just mock ResizeObserver and PointerCapture.
// This is the standard way to test Radix.

describe("InviteModal", () => {
  const mockCreateInvitation = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useCreateInvitation as any).mockReturnValue({
      mutate: mockCreateInvitation,
      isPending: false,
    });
    (useCurrentOrg as any).mockReturnValue({
      organization: { id: "org-123", name: "Test Org" },
    });

    // Mock pointer capture for Radix
    window.HTMLElement.prototype.setPointerCapture = vi.fn();
    window.HTMLElement.prototype.releasePointerCapture = vi.fn();
    window.HTMLElement.prototype.hasPointerCapture = vi.fn();
  });

  // Unmock UI for this test to rely on real Radix behavior
  vi.unmock("../ui/dialog");

  it("opens and submits invitation", async () => {
    const user = userEvent.setup();
    render(<InviteModal />);

    // 1. Check Trigger
    const inviteBtn = screen.getByRole("button", { name: /invite member/i });
    expect(inviteBtn).toBeInTheDocument();

    // 2. Open Modal
    await user.click(inviteBtn);

    // 3. Check Form Content (Header)
    expect(await screen.findByText("Invite Team Member")).toBeInTheDocument();

    // 4. Fill Form
    const emailInput = screen.getByLabelText(/email address/i);
    await user.type(emailInput, "test@example.com");

    const roleSelect = screen.getByLabelText(/role/i);
    await user.selectOptions(roleSelect, "ADMIN");

    // 5. Submit
    const submitBtn = screen.getByRole("button", { name: "Send Invitation" });
    await user.click(submitBtn);

    // 6. Verify Hook Call
    await waitFor(() => {
      expect(mockCreateInvitation).toHaveBeenCalledWith(
        { email: "test@example.com", role: "ADMIN" },
        expect.any(Object),
      );
    });
  });
});
