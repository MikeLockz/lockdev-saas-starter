import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as useCurrentOrgHook from "@/hooks/useCurrentOrg";
import * as useUserProfileHook from "@/hooks/useUserProfile";
import { OrgSwitcher } from "../OrgSwitcher";

// Mock the hooks
vi.mock("@/hooks/useCurrentOrg", () => ({
  useCurrentOrg: vi.fn(),
}));

vi.mock("@/hooks/useUserProfile", () => ({
  useUserProfile: vi.fn(),
}));

// Mock ResizeObserver
(globalThis as any).ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

window.HTMLElement.prototype.scrollIntoView = vi.fn();
window.HTMLElement.prototype.hasPointerCapture = vi.fn();
window.HTMLElement.prototype.releasePointerCapture = vi.fn();

// Mock PointerEvent
vi.stubGlobal("PointerEvent", class PointerEvent extends Event {});

describe("OrgSwitcher", () => {
  const mockSetCurrentOrgId = vi.fn();
  const mockOrgs = [
    { id: "1", name: "Org 1", slug: "org-1" },
    { id: "2", name: "Org 2", slug: "org-2" },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementation for useUserProfile
    (useUserProfileHook.useUserProfile as any).mockReturnValue({
      profile: { is_super_admin: false },
    });
  });

  it("renders current org name", () => {
    (useCurrentOrgHook.useCurrentOrg as any).mockReturnValue({
      organization: mockOrgs[0],
      organizations: mockOrgs,
      setCurrentOrgId: mockSetCurrentOrgId,
      isLoading: false,
    });

    render(<OrgSwitcher />);
    expect(screen.getByText("Org 1")).toBeDefined();
  });

  it("renders placeholder when no org selected", () => {
    (useCurrentOrgHook.useCurrentOrg as any).mockReturnValue({
      organization: null,
      organizations: [],
      setCurrentOrgId: mockSetCurrentOrgId,
      isLoading: false,
    });

    render(<OrgSwitcher />);
    expect(screen.getByText("Select Organization")).toBeDefined();
  });

  it.skip("lists available organizations", async () => {
    const user = userEvent.setup();
    (useCurrentOrgHook.useCurrentOrg as any).mockReturnValue({
      organization: mockOrgs[0],
      organizations: mockOrgs,
      setCurrentOrgId: mockSetCurrentOrgId,
      isLoading: false,
    });

    render(<OrgSwitcher />);

    const trigger = screen.getByRole("combobox");
    await user.click(trigger);

    expect(await screen.findByText("Org 1")).toBeDefined();
  });

  it.skip("calls setCurrentOrgId when org is selected", async () => {
    const user = userEvent.setup();
    (useCurrentOrgHook.useCurrentOrg as any).mockReturnValue({
      organization: mockOrgs[0], // Currently selected: Org 1
      organizations: mockOrgs,
      setCurrentOrgId: mockSetCurrentOrgId,
      isLoading: false,
    });

    render(<OrgSwitcher />);

    const trigger = screen.getByRole("combobox");
    await user.click(trigger);

    // Find the option for Org 2
    const org2Option = await screen.findByText("Org 2");
    await user.click(org2Option);

    expect(mockSetCurrentOrgId).toHaveBeenCalledWith("2");
  });
});
