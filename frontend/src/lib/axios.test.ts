import { describe, expect, it } from "vitest";
import api from "./axios";

describe("Axios Security Interceptor", () => {
  it("allows relative requests", async () => {
    // We just want to check if it DOES NOT throw
    const config = { url: "/api/health" };
    const interceptor = (api.interceptors.request as any).handlers[0].fulfilled;
    const result = interceptor(config);
    expect(result).toBe(config);
  });

  it("allows requests to allowed domains (localhost)", async () => {
    const config = { url: "http://localhost:8000/health" };
    const interceptor = (api.interceptors.request as any).handlers[0].fulfilled;
    const result = interceptor(config);
    expect(result).toBe(config);
  });

  it("blocks requests to evil.com", async () => {
    const config = { url: "http://evil.com/malware" };
    const interceptor = (api.interceptors.request as any).handlers[0].fulfilled;
    expect(() => interceptor(config)).toThrow(
      "External request to evil.com is blocked by security policy.",
    );
  });
});
