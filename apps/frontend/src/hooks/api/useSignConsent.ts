import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";

export const useSignConsent = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (documentId: string) => {
      const response = await api.post("/api/v1/consent", {
        document_id: documentId,
      });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate consent queries to refresh the list
      queryClient.invalidateQueries({ queryKey: ["requiredConsents"] });
      // Also invalidate user profile as requires_consent flag may have changed
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
    },
  });
};
