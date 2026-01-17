import api from "@/lib/axios";

export const useAnalytics = () => {
  const track = async (event: string, properties: Record<string, any> = {}) => {
    try {
      // Use relative path or full URL depending on baseURL configuration
      await api.post("/telemetry", { event, ...properties });
    } catch (error) {
      // Fail silently in production, or log to console in dev
      console.error("TELEMETRY_ERROR", error);
    }
  };

  const pageView = (path: string) => track("PAGE_VIEW", { path });
  const trackClick = (element: string) => track("CLICK", { element });
  const trackError = (error: string, component?: string) =>
    track("ERROR", { message: error, component });

  return {
    track,
    pageView,
    trackClick,
    trackError,
  };
};
