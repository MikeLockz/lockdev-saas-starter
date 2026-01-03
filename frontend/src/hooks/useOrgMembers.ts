import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useAuth } from './useAuth';
import type { components } from '@/lib/api-types';

export type Member = components['schemas']['MemberRead'];

export function useOrgMembers(orgId: string | null) {
    const { user } = useAuth();

    return useQuery<Member[]>({
        queryKey: ['orgMembers', orgId],
        queryFn: async () => {
            if (!user || !orgId) return [];
            const token = await user.getIdToken();
            const response = await api.get(`/api/v1/organizations/${orgId}/members`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            return response.data;
        },
        enabled: !!user && !!orgId,
    });
}
