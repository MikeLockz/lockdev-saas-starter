import { beforeEach, describe, expect, it } from "vitest";
import { useAuthStore } from "../auth-store";

describe("Auth Store", () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isImpersonating: false,
    });
  });

  it("has correct initial state", () => {
    const state = useAuthStore.getState();
    // Snapshot only serializable state
    expect({
      user: state.user,
      isAuthenticated: state.isAuthenticated,
      isImpersonating: state.isImpersonating,
    }).toMatchSnapshot();
  });

  it("state after login with user profile", () => {
    const { setUser } = useAuthStore.getState();
    setUser({
      id: "user-123",
      email: "test@example.com",
      full_name: "Test User",
      role: "patient",
      roles: ["patient"],
      mfa_enabled: false,
      requires_consent: false,
    });

    const state = useAuthStore.getState();
    expect({
      user: state.user,
      isAuthenticated: state.isAuthenticated,
      isImpersonating: state.isImpersonating,
    }).toMatchSnapshot();
  });

  it("state after logout", () => {
    const { setUser, logout } = useAuthStore.getState();
    // First login
    setUser({
      id: "user-123",
      email: "test@example.com",
      full_name: "Test User",
    });
    // Then logout
    logout();

    const state = useAuthStore.getState();
    expect({
      user: state.user,
      isAuthenticated: state.isAuthenticated,
      isImpersonating: state.isImpersonating,
    }).toMatchSnapshot();
  });

  it("state while impersonating", () => {
    const { setUser, setImpersonating } = useAuthStore.getState();
    setUser({
      id: "admin-123",
      email: "admin@example.com",
      full_name: "Admin User",
      roles: ["super_admin"],
    });
    setImpersonating(true);

    const state = useAuthStore.getState();
    expect({
      user: state.user,
      isAuthenticated: state.isAuthenticated,
      isImpersonating: state.isImpersonating,
    }).toMatchSnapshot();
  });
});
