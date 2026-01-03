import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useOrgStore } from '@/store/org-store';

export type StaffMember = {
    id: string;
    user_id: string;
    organization_id: string;
    email: string;
    display_name: string;
    role: string;
    created_at: string;
    name: string; // Helper for display
};

export const useStaff = () => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery({
        queryKey: ['staff', currentOrgId],
        queryFn: async () => {
            if (!currentOrgId) return [];
            const response = await api.get(`/api/v1/organizations/${currentOrgId}/members`);
            // Map to add 'name' helper
            return response.data.map((m: any) => ({
                ...m,
                name: m.display_name || m.email
            })) as StaffMember[];
        },
        enabled: !!currentOrgId
    });
};
