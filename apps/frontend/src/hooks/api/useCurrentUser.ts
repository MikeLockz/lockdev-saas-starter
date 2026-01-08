import { useQuery } from "@tanstack/react-query";
import { isUnauthorizedError } from "@/lib/api-error";
import { api } from "@/lib/axios";
import type { User } from "@/lib/models";

export const useCurrentUser = () => {
  return useQuery<User>({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const response = await api.get("/api/v1/users/me");
      return response.data;
    },
    // Don't retry on 401s as it usually means not logged in
    retry: (failureCount, error) => {
      if (isUnauthorizedError(error)) return false;
      return failureCount < 2;
    },
  });
};
