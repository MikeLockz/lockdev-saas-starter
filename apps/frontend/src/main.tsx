import { QueryClientProvider } from "@tanstack/react-query";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { TimezoneProvider } from "@/contexts/TimezoneContext";
import { queryClient } from "@/lib/query-client";
import { routeTree } from "./routeTree.gen";
import "./index.css";
import * as Sentry from "@sentry/react";

// Sentry Initialization
if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration(),
    ],
    // Tracing
    tracesSampleRate: 1.0,
    // Session Replay
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
    // PII
    sendDefaultPii: false,
  });
}

// Create a new router instance
const router = createRouter({ routeTree });

// Register the router instance for type safety
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <TimezoneProvider>
        <RouterProvider router={router} />
      </TimezoneProvider>
    </QueryClientProvider>
  </StrictMode>,
);
