import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import type { Member } from "@/lib/models";
import { useAuth } from "./useAuth";

export type { Member };

export function useOrgMembers(orgId: string | null) {
  const { user } = useAuth();

  return useQuery<Member[]>({
    queryKey: ["orgMembers", orgId],
    queryFn: async () => {
      if (!user || !orgId) return [];
      const token = await user.getIdToken();
      const response = await api.get(`/api/v1/organizations/${orgId}/members`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
    enabled: !!user && !!orgId,
  });
}
