import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useAuth } from './useAuth';
import type { components } from '@/lib/api-types';

export type Organization = components['schemas']['OrganizationRead'];

export function useOrganizations() {
    const { user } = useAuth();

    return useQuery<Organization[]>({
        queryKey: ['organizations'],
        queryFn: async () => {
            // Return empty if no user, but enabled check handles this mostly
            if (!user) return [];
            const token = await user.getIdToken();
            const response = await api.get('/api/v1/organizations', {
                headers: { Authorization: `Bearer ${token}` },
            });
            return response.data;
        },
        enabled: !!user,
        staleTime: 5 * 60 * 1000, // 5 minutes cache
    });
}
