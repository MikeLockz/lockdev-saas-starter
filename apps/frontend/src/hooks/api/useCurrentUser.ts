import { useQuery } from "@tanstack/react-query";
import type { components } from "@/lib/api-types";
import { api } from "@/lib/axios";

type UserRead = components["schemas"]["UserRead"];

export const useCurrentUser = () => {
  return useQuery<UserRead>({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const response = await api.get("/api/v1/users/me");
      return response.data;
    },
    // Don't retry on 401s as it usually means not logged in
    retry: (failureCount, error: any) => {
      if (error?.response?.status === 401) return false;
      return failureCount < 2;
    },
  });
};
