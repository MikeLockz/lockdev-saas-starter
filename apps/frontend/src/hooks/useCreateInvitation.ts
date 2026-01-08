import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import type { InvitationCreate } from "@/lib/models";

export const useCreateInvitation = (orgId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: InvitationCreate) => {
      const response = await api.post(
        `/api/v1/organizations/${orgId}/invitations`,
        data,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["organizations", orgId, "invitations"],
      });
    },
  });
};
