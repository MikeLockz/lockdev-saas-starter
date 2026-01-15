import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import type { Member } from "@/lib/models";

export const useOrgMembers = (orgId: string | undefined) => {
  return useQuery<Member[]>({
    queryKey: ["org-members", orgId],
    queryFn: async () => {
      if (!orgId) throw new Error("Organization ID is required");
      const response = await api.get(`/api/v1/organizations/${orgId}/members`);
      return response.data;
    },
    enabled: !!orgId,
  });
};
