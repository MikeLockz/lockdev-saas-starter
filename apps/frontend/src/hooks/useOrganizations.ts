import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import type { Organization } from "@/lib/models";
import { useAuth } from "./useAuth";

export type { Organization };

export interface UseOrganizationsOptions {
  forSuperAdmin?: boolean;
}

export function useOrganizations(options?: UseOrganizationsOptions) {
  const { user } = useAuth();
  const forSuperAdmin = options?.forSuperAdmin ?? false;

  return useQuery<Organization[]>({
    queryKey: ["organizations", { forSuperAdmin }],
    queryFn: async () => {
      // Return empty if no user, but enabled check handles this mostly
      if (!user) return [];
      const token = await user.getIdToken();
      const endpoint = forSuperAdmin
        ? "/api/v1/admin/super-admin/organizations"
        : "/api/v1/organizations";
      const response = await api.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` },
      });
      // Super admin endpoint returns { items: [...], total, page, page_size }
      return forSuperAdmin ? response.data.items : response.data;
    },
    enabled: !!user,
    staleTime: 5 * 60 * 1000, // 5 minutes cache
  });
}
