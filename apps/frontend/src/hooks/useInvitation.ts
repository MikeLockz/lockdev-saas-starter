import { useQuery } from "@tanstack/react-query";
import type { components } from "@/lib/api-types";
import { api } from "@/lib/axios";

type InvitationRead = components["schemas"]["InvitationRead"];

export const useInvitation = (token: string) => {
  return useQuery<InvitationRead>({
    queryKey: ["invitation", token],
    queryFn: async () => {
      const response = await api.get(`/api/v1/invitations/${token}`);
      return response.data;
    },
    enabled: !!token,
    retry: false, // Don't retry if token is invalid
  });
};
