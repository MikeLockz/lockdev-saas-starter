import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as useCurrentOrgHook from "@/hooks/useCurrentOrg";
import * as useOrgMembersHook from "@/hooks/useOrgMembers";
import { MemberTable } from "../MemberTable";

// Mock hooks
vi.mock("@/hooks/useCurrentOrg", () => ({
  useCurrentOrg: vi.fn(),
}));

vi.mock("@/hooks/useOrgMembers", () => ({
  useOrgMembers: vi.fn(),
}));

describe("MemberTable", () => {
  const mockMembers = [
    {
      id: "1",
      email: "alice@example.com",
      role: "ADMIN",
      created_at: "2023-01-01T00:00:00Z",
      display_name: "Alice",
    },
    {
      id: "2",
      email: "bob@example.com",
      role: "MEMBER",
      created_at: "2023-01-02T00:00:00Z",
      display_name: null,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state", () => {
    (useCurrentOrgHook.useCurrentOrg as any).mockReturnValue({ orgId: "org1" });
    (useOrgMembersHook.useOrgMembers as any).mockReturnValue({
      data: undefined,
      isLoading: true,
    });

    const { container } = render(<MemberTable />);
    // Checking for skeleton or text
    // Since we used Skeleton component which might not render text, we check for class or structure
    // But simply checking it doesn't crash and renders something different than empty
    // The skeleton has class 'animate-pulse' usually
    expect(
      container.getElementsByClassName("animate-pulse").length,
    ).toBeGreaterThan(0);
  });

  it("renders empty state", () => {
    (useCurrentOrgHook.useCurrentOrg as any).mockReturnValue({ orgId: "org1" });
    (useOrgMembersHook.useOrgMembers as any).mockReturnValue({
      data: [],
      isLoading: false,
    });

    render(<MemberTable />);
    expect(
      screen.getByText("No members found in this organization."),
    ).toBeDefined();
  });

  it("renders member list", () => {
    (useCurrentOrgHook.useCurrentOrg as any).mockReturnValue({ orgId: "org1" });
    (useOrgMembersHook.useOrgMembers as any).mockReturnValue({
      data: mockMembers,
      isLoading: false,
    });

    render(<MemberTable />);

    expect(screen.getByText("Alice")).toBeDefined();
    expect(screen.getByText("alice@example.com")).toBeDefined();
    // Capitalized
    expect(screen.getByText("ADMIN")).toBeDefined();

    // Bob has no display name, so checks fallback or just email
    // Our component logic: member.display_name || "Unknown" - wait, let me check component
    // member.display_name || "Unknown"
    // But Bob has display_name: null. So "Unknown".
    // Wait, "Unknown" is a reasonable fallback.
    expect(screen.getAllByText("bob@example.com").length).toBeGreaterThan(0);
  });
});
