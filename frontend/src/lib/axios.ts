import { auth } from "@/lib/firebase";
import { useOrgStore } from "@/store/org-store";
import axios from "axios";

const ALLOWED_DOMAINS = [window.location.hostname, "localhost", "127.0.0.1"];

export const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL as string) || "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(async (config) => {
  // Add Org ID if available
  const currentOrg = useOrgStore.getState().currentOrg;
  if (currentOrg) {
    config.headers["X-Organization-Id"] = currentOrg.id;
  }

  // Add JWT Token if available
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (config.url?.startsWith("http")) {
    const url = new URL(config.url);
    if (!ALLOWED_DOMAINS.includes(url.hostname)) {
      throw new Error(`External request to ${url.hostname} is blocked by security policy.`);
    }
  }
  return config;
});

export default api;
