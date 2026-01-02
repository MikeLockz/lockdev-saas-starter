import axios from "axios";

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
  (config) => {
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
