import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useCurrentOrg } from "./useCurrentOrg";

// Types
export interface Provider {
  id: string;
  user_id: string;
  organization_id: string;
  npi_number: string | null;
  specialty: string | null;
  license_number: string | null;
  license_state: string | null;
  dea_number: string | null;
  state_licenses: unknown[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user_email: string | null;
  user_display_name: string | null;
}

export interface ProviderListItem {
  id: string;
  user_id: string;
  npi_number: string | null;
  specialty: string | null;
  is_active: boolean;
  user_email: string | null;
  user_display_name: string | null;
}

export interface PaginatedProviders {
  items: ProviderListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface ProviderCreate {
  user_id: string;
  npi_number?: string;
  specialty?: string;
  license_number?: string;
  license_state?: string;
  dea_number?: string;
}

export interface ProviderUpdate {
  npi_number?: string;
  specialty?: string;
  license_number?: string;
  license_state?: string;
  dea_number?: string;
  is_active?: boolean;
}

// Hooks
export function useProviders(options?: {
  specialty?: string;
  isActive?: boolean;
}) {
  const { orgId } = useCurrentOrg();

  return useQuery<PaginatedProviders>({
    queryKey: ["providers", orgId, options],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (options?.specialty) params.set("specialty", options.specialty);
      if (options?.isActive !== undefined)
        params.set("is_active", String(options.isActive));

      const response = await api.get(
        `/api/v1/organizations/${orgId}/providers?${params}`,
      );
      return response.data;
    },
    enabled: !!orgId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useProvider(providerId: string | undefined) {
  const { orgId } = useCurrentOrg();

  return useQuery<Provider>({
    queryKey: ["provider", orgId, providerId],
    queryFn: async () => {
      const response = await api.get(
        `/api/v1/organizations/${orgId}/providers/${providerId}`,
      );
      return response.data;
    },
    enabled: !!orgId && !!providerId,
  });
}

export function useCreateProvider() {
  const queryClient = useQueryClient();
  const { orgId } = useCurrentOrg();

  return useMutation({
    mutationFn: async (data: ProviderCreate) => {
      const response = await api.post(
        `/api/v1/organizations/${orgId}/providers`,
        data,
      );
      return response.data as Provider;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["providers", orgId] });
    },
  });
}

export function useUpdateProvider() {
  const queryClient = useQueryClient();
  const { orgId } = useCurrentOrg();

  return useMutation({
    mutationFn: async ({
      providerId,
      data,
    }: {
      providerId: string;
      data: ProviderUpdate;
    }) => {
      const response = await api.patch(
        `/api/v1/organizations/${orgId}/providers/${providerId}`,
        data,
      );
      return response.data as Provider;
    },
    onSuccess: (_, { providerId }) => {
      queryClient.invalidateQueries({ queryKey: ["providers", orgId] });
      queryClient.invalidateQueries({
        queryKey: ["provider", orgId, providerId],
      });
    },
  });
}

export function useDeleteProvider() {
  const queryClient = useQueryClient();
  const { orgId } = useCurrentOrg();

  return useMutation({
    mutationFn: async (providerId: string) => {
      await api.delete(
        `/api/v1/organizations/${orgId}/providers/${providerId}`,
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["providers", orgId] });
    },
  });
}

/**
 * Get the provider profile for the current user.
 * Returns undefined if the current user is not a provider.
 */
export function useCurrentUserProvider() {
  const { orgId } = useCurrentOrg();
  const { data: providers, isLoading } = useProviders();

  return useQuery<Provider | null>({
    queryKey: ["current-user-provider", orgId],
    queryFn: async () => {
      // Get current user ID
      const userResponse = await api.get("/api/v1/users/me");
      const userId = userResponse.data?.id;

      if (!userId || !providers?.items) return null;

      // Find provider matching current user
      const match = providers.items.find((p) => p.user_id === userId);
      if (!match) return null;

      // Fetch full provider details
      const response = await api.get(
        `/api/v1/organizations/${orgId}/providers/${match.id}`,
      );
      return response.data;
    },
    enabled: !!orgId && !isLoading && !!providers?.items?.length,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
