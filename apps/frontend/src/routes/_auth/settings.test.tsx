import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as useAuthHook from "@/hooks/useAuth";
import { Settings } from "./settings";

// Mock child components
vi.mock("@/components/settings", () => ({
  ProfileForm: () => <div data-testid="profile-form">Profile Form</div>,
  SessionList: () => <div data-testid="session-list">Session List</div>,
  MFASetup: () => <div data-testid="mfa-setup">MFA Setup</div>,
  TimezonePreferences: () => (
    <div data-testid="timezone-preferences">Timezone Preferences</div>
  ),
  PreferencesForm: () => (
    <div data-testid="preferences-form">Preferences Form</div>
  ),
}));

vi.mock("@/components/ui/button", () => ({
  Button: ({
    onClick,
    children,
  }: {
    onClick: () => void;
    children: ReactNode;
  }) => <button onClick={onClick}>{children}</button>,
}));

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: () => () => ({}),
  Link: ({ children }: { children: React.ReactNode }) => (
    <a href="/">{children}</a>
  ),
}));

describe("Settings Page", () => {
  const mockSignOut = vi.fn();
  const mockUser = { email: "test@example.com" };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(useAuthHook, "useAuth").mockReturnValue({
      user: mockUser,
      signOut: mockSignOut,
    } as unknown as ReturnType<typeof useAuthHook.useAuth>);
  });

  it("renders settings header and default profile tab", () => {
    render(<Settings />);

    expect(screen.getByText("Settings")).toBeInTheDocument();
    expect(
      screen.getByText("Manage your account settings and preferences"),
    ).toBeInTheDocument();
    expect(screen.getByText("test@example.com")).toBeInTheDocument();
    expect(screen.getByText("Profile")).toBeInTheDocument();
    expect(screen.getByTestId("profile-form")).toBeInTheDocument();
  });

  it("switches tabs correctly", () => {
    render(<Settings />);

    // Switch to Security tab
    fireEvent.click(screen.getByText("Security"));
    expect(screen.getByTestId("session-list")).toBeInTheDocument();
    expect(screen.getByTestId("mfa-setup")).toBeInTheDocument();
    expect(screen.queryByTestId("profile-form")).not.toBeInTheDocument();

    // Switch to Privacy tab
    fireEvent.click(screen.getByText("Privacy"));
    expect(screen.getByTestId("timezone-preferences")).toBeInTheDocument();
    expect(screen.getByTestId("preferences-form")).toBeInTheDocument();
    expect(screen.queryByTestId("session-list")).not.toBeInTheDocument();
  });

  it("handles logout", async () => {
    render(<Settings />);

    const logoutButton = screen.getByText("Logout");
    fireEvent.click(logoutButton);

    await waitFor(() => {
      expect(mockSignOut).toHaveBeenCalled();
    });
  });
});
