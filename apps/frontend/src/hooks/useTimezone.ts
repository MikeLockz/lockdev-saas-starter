/**
 * Hook to get the current user's effective timezone.
 */
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";

interface TimezoneResponse {
  timezone: string;
  source: "user" | "organization";
}

const DEFAULT_TIMEZONE = "America/New_York";

/**
 * Fetch the user's effective timezone from the API.
 * Falls back to default if not authenticated.
 */
export function useTimezone(): string {
  const { data } = useQuery<TimezoneResponse>({
    queryKey: ["userTimezone"],
    queryFn: async () => {
      const response = await api.get("/api/v1/users/me/timezone");
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    retry: false, // Don't retry on 401
  });

  return data?.timezone || DEFAULT_TIMEZONE;
}

/**
 * Get timezone with source information.
 */
export function useTimezoneWithSource() {
  return useQuery<TimezoneResponse>({
    queryKey: ["userTimezone"],
    queryFn: async () => {
      const response = await api.get("/api/v1/users/me/timezone");
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}
