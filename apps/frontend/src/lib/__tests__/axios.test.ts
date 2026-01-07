import MockAdapter from "axios-mock-adapter";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useOrgStore } from "@/store/org-store";
import { api } from "../axios";
import { auth } from "../firebase";

// Mock Firebase Auth
vi.mock("../firebase", () => ({
  auth: {
    currentUser: null,
  },
}));

// Mock Org Store
vi.mock("@/store/org-store", () => ({
  useOrgStore: {
    getState: vi.fn(() => ({ currentOrgId: null })),
  },
}));

describe("Axios Interceptors", () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(api);
    vi.clearAllMocks();
  });

  afterEach(() => {
    mock.restore();
  });

  it("should add Authorization header when user is logged in", async () => {
    // Setup Mock Auth
    const getIdTokenMock = vi.fn().mockResolvedValue("mock-token");
    // @ts-expect-error
    auth.currentUser = { getIdToken: getIdTokenMock };

    // Setup Mock Request
    mock.onGet("/test").reply(200, {});

    await api.get("/test");

    expect(getIdTokenMock).toHaveBeenCalled();
    expect(mock.history.get[0].headers).toHaveProperty(
      "Authorization",
      "Bearer mock-token",
    );
  });

  it("should add X-Organization-Id header when org is selected", async () => {
    // Setup Mock Org Store
    vi.mocked(useOrgStore.getState).mockReturnValue({
      currentOrgId: "org-123",
    } as any);

    mock.onGet("/test").reply(200, {});

    await api.get("/test");

    expect(mock.history.get[0].headers).toHaveProperty(
      "X-Organization-Id",
      "org-123",
    );
  });

  it("scrolls through allowed domains (sanity check on interceptor logic)", async () => {
    // No auth, no org
    (auth as any).currentUser = null;
    vi.mocked(useOrgStore.getState).mockReturnValue({
      currentOrgId: null,
    } as any);

    mock.onGet("/test").reply(200);
    const res = await api.get("/test");
    expect(res.status).toBe(200);
  });
});
