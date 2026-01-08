import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import type { Organization } from "@/lib/models";

export const useOrganizations = () => {
  return useQuery<Organization[]>({
    queryKey: ["organizations"],
    queryFn: async () => {
      const response = await api.get("/api/v1/organizations/");
      return response.data;
    },
  });
};
