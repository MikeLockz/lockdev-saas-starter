import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import type { components } from "@/lib/api-types";

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
