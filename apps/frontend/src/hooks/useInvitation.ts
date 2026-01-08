import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import type { Invitation } from "@/lib/models";

export const useInvitation = (token: string) => {
  return useQuery<Invitation>({
    queryKey: ["invitation", token],
    queryFn: async () => {
      const response = await api.get(`/api/v1/invitations/${token}`);
      return response.data;
    },
    enabled: !!token,
    retry: false, // Don't retry if token is invalid
  });
};
