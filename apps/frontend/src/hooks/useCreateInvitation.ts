import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { components } from "@/lib/api-types";
import { api } from "@/lib/axios";

type InvitationCreate = components["schemas"]["InvitationCreate"];

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
