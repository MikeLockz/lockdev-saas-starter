import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import MockAdapter from "axios-mock-adapter";
import type React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/axios";
import { useCurrentUser } from "../useCurrentUser";

// Mock Org Store to prevent issues in axios interceptor
vi.mock("@/store/org-store", () => ({
  useOrgStore: {
    getState: vi.fn(() => ({ currentOrgId: null })),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("useCurrentUser", () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(api);
  });

  afterEach(() => {
    mock.restore();
  });

  it("fetches current user successfully", async () => {
    const mockUser = {
      id: "1",
      email: "test@example.com",
      full_name: "Test User",
    };
    mock.onGet("/api/v1/users/me").reply(200, mockUser);

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockUser);
  });

  it("handles errors", async () => {
    mock.onGet("/api/v1/users/me").reply(500);

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true), {
      timeout: 5000,
    });
  });
});
