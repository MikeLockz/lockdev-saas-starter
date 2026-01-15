import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { api } from "@/lib/axios";

export const useAcceptInvitation = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (token: string) => {
      const response = await api.post(`/api/v1/invitations/${token}/accept`);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate user queries to refresh permissions/org memberships
      queryClient.invalidateQueries({ queryKey: ["users", "me"] });
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      navigate({ to: "/dashboard" });
    },
  });
};
