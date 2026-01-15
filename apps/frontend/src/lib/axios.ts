import axios from "axios";
import { auth } from "@/lib/firebase";
import { useOrgStore } from "@/store/org-store";

// Whitelist of allowed domains
const ALLOWED_DOMAINS = [
  "localhost",
  "127.0.0.1",
  "lockdev.com", // Example production domain
  // Add other allowed domains here
];

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  async (config) => {
    // 1. Inject Organization ID
    const currentOrgId = useOrgStore.getState().currentOrgId;
    if (currentOrgId && config.headers) {
      config.headers["X-Organization-Id"] = currentOrgId;
    }

    // 2. Inject Auth Token
    if (auth.currentUser && config.headers) {
      try {
        const token = await auth.currentUser.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      } catch (error) {
        console.warn("Failed to get ID token", error);
        // Continue without token, let backend handle 401
      }
    } else if (config.headers) {
      // Check for mock user in localStorage (for local development)
      const mockUserJson = localStorage.getItem("lockdev_mock_user");
      if (mockUserJson) {
        try {
          const mockUser = JSON.parse(mockUserJson);
          if (mockUser.email) {
            config.headers.Authorization = `Bearer mock_${mockUser.email}`;
          }
        } catch {
          // Invalid JSON, ignore
        }
      }
    }

    // 3. Security Check
    if (config.url) {
      try {
        // Handle relative URLs (they are safe as they go to baseURL)
        if (config.url.startsWith("/") || !config.url.startsWith("http")) {
          return config;
        }

        const url = new URL(config.url);
        const hostname = url.hostname;

        const isAllowed = ALLOWED_DOMAINS.some(
          (domain) => hostname === domain || hostname.endsWith(`.${domain}`),
        );

        if (!isAllowed) {
          // Return a rejected promise to cancel the request
          return Promise.reject(
            new Error(`Security Error: Request to ${hostname} is blocked.`),
          );
        }
      } catch (error) {
        // If URL parsing fails or blocked, reject request
        return Promise.reject(error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Add response interceptor for global error handling (optional but good practice)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access (e.g., redirect to login)
      // For now, we rely on the component or router to handle 401s,
      // but we could dispatch a global event here.
    }
    return Promise.reject(error);
  },
);
