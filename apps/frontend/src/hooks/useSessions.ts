import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useAuth } from "./useAuth";

// Types
export interface Session {
  id: string;
  device: string;
  ip_address: string;
  location?: string;
  is_current: boolean;
  created_at: string;
  last_active_at: string;
}

export interface SessionListResponse {
  items: Session[];
  total: number;
  limit: number;
  offset: number;
}

export function useSessions() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery<SessionListResponse>({
    queryKey: ["sessions"],
    queryFn: async () => {
      const token = await user?.getIdToken();
      const response = await api.get("/api/v1/users/me/sessions", {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
    enabled: !!user,
    staleTime: 60 * 1000, // 1 minute
  });

  const revokeSession = useMutation({
    mutationFn: async (sessionId: string) => {
      const token = await user?.getIdToken();
      const response = await api.delete(
        `/api/v1/users/me/sessions/${sessionId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });

  return {
    sessions: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    revokeSession,
  };
}
