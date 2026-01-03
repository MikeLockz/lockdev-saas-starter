import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useCurrentOrg } from './useCurrentOrg';

// Types
export interface CareTeamProviderInfo {
    id: string;
    user_id: string;
    npi_number: string | null;
    specialty: string | null;
    user_display_name: string | null;
    user_email: string | null;
}

export interface CareTeamMember {
    assignment_id: string;
    provider_id: string;
    role: 'PRIMARY' | 'SPECIALIST' | 'CONSULTANT';
    assigned_at: string;
    provider_name: string | null;
    provider_specialty: string | null;
    provider_npi: string | null;
}

export interface CareTeamList {
    patient_id: string;
    members: CareTeamMember[];
    primary_provider: CareTeamMember | null;
}

export interface CareTeamAssignment {
    id: string;
    patient_id: string;
    provider_id: string;
    role: string;
    assigned_at: string;
    removed_at: string | null;
    provider: CareTeamProviderInfo;
}

export interface CareTeamAssignmentCreate {
    provider_id: string;
    role: 'PRIMARY' | 'SPECIALIST' | 'CONSULTANT';
}

// Hooks
export function useCareTeam(patientId: string | undefined) {
    const { orgId } = useCurrentOrg();

    return useQuery<CareTeamList>({
        queryKey: ['careTeam', orgId, patientId],
        queryFn: async () => {
            const response = await api.get(
                `/api/v1/organizations/${orgId}/patients/${patientId}/care-team`
            );
            return response.data;
        },
        enabled: !!orgId && !!patientId,
        staleTime: 60 * 1000, // 1 minute
    });
}

export function useAssignToCareTeam() {
    const queryClient = useQueryClient();
    const { orgId } = useCurrentOrg();

    return useMutation({
        mutationFn: async ({ patientId, data }: { patientId: string; data: CareTeamAssignmentCreate }) => {
            const response = await api.post(
                `/api/v1/organizations/${orgId}/patients/${patientId}/care-team`,
                data
            );
            return response.data as CareTeamAssignment;
        },
        onSuccess: (_, { patientId }) => {
            queryClient.invalidateQueries({ queryKey: ['careTeam', orgId, patientId] });
        },
    });
}

export function useRemoveFromCareTeam() {
    const queryClient = useQueryClient();
    const { orgId } = useCurrentOrg();

    return useMutation({
        mutationFn: async ({ patientId, assignmentId }: { patientId: string; assignmentId: string }) => {
            await api.delete(
                `/api/v1/organizations/${orgId}/patients/${patientId}/care-team/${assignmentId}`
            );
        },
        onSuccess: (_, { patientId }) => {
            queryClient.invalidateQueries({ queryKey: ['careTeam', orgId, patientId] });
        },
    });
}
