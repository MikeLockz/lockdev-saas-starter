import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useOrgStore } from '@/store/org-store';
import { toast } from 'sonner';

export type Call = {
    id: string;
    organization_id: string;
    agent_id: string;
    patient_id?: string;
    direction: 'INBOUND' | 'OUTBOUND';
    status: 'QUEUED' | 'IN_PROGRESS' | 'COMPLETED' | 'MISSED';
    phone_number: string;
    started_at?: string;
    ended_at?: string;
    duration_seconds?: number;
    notes?: string;
    outcome?: string;
    patient_name?: string;
    agent_name?: string;
    created_at: string;
};

export type CreateCallData = {
    direction: 'INBOUND' | 'OUTBOUND';
    phone_number: string;
    patient_id?: string;
    notes?: string;
    outcome?: string;
};

export type UpdateCallData = {
    status?: string;
    notes?: string;
    outcome?: string;
};

export const useCalls = (filters?: { status?: string; agent_id?: string }) => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);
    return useQuery({
        queryKey: ['calls', currentOrgId, filters],
        queryFn: async () => {
            if (!currentOrgId) return [];
            const params = new URLSearchParams();
            if (filters?.status) params.append('status', filters.status);
            if (filters?.agent_id) params.append('agent_id', filters.agent_id);

            const response = await api.get<Call[]>(`/api/v1/organizations/${currentOrgId}/calls?${params.toString()}`);
            return response.data;
        },
        enabled: !!currentOrgId,
    });
};

export const useCreateCall = () => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: CreateCallData) => {
            if (!currentOrgId) throw new Error('No organization selected');
            const response = await api.post<Call>(`/api/v1/organizations/${currentOrgId}/calls`, data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['calls'] });
            toast.success('Call logged successfully');
        },
        onError: () => {
            toast.error('Failed to log call');
        },
    });
};

export const useUpdateCall = () => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({ id, data }: { id: string; data: UpdateCallData }) => {
            if (!currentOrgId) throw new Error('No organization selected');
            const response = await api.patch<Call>(`/api/v1/organizations/${currentOrgId}/calls/${id}`, data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['calls'] });
            toast.success('Call updated successfully');
        },
        onError: () => {
            toast.error('Failed to update call');
        },
    });
};
