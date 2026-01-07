import { useQuery } from "@tanstack/react-query";
import type { components } from "@/lib/api-types";
import { api } from "@/lib/axios";

type OrganizationRead = components["schemas"]["OrganizationRead"];

export const useOrganizations = () => {
  return useQuery<OrganizationRead[]>({
    queryKey: ["organizations"],
    queryFn: async () => {
      const response = await api.get("/api/v1/organizations/");
      return response.data;
    },
  });
};
