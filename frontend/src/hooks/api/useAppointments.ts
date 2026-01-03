import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useOrgStore } from '@/store/org-store';

// Types
export interface Appointment {
    id: string;
    organization_id: string;
    patient_id: string;
    provider_id: string;
    scheduled_at: string;
    duration_minutes: number;
    appointment_type: string;
    reason: string | null;
    notes: string | null;
    status: string;
    cancelled_at: string | null;
    cancelled_by: string | null;
    cancellation_reason: string | null;
    created_at: string;
    updated_at: string;
    patient_name: string | null;
    provider_name: string | null;
}

export interface PaginatedAppointments {
    items: Appointment[];
    total: number;
    limit: number;
    offset: number;
}

export interface AppointmentSearchParams {
    date_from?: string;
    date_to?: string;
    provider_id?: string;
    patient_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
}

export interface AppointmentCreate {
    patient_id: string;
    provider_id: string;
    scheduled_at: string;
    duration_minutes?: number;
    appointment_type?: string;
    reason?: string;
    notes?: string;
}

export interface AppointmentStatusUpdate {
    status: string;
    cancellation_reason?: string;
}

// Hooks
export function useAppointments(params: AppointmentSearchParams = {}) {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<PaginatedAppointments>({
        queryKey: ['appointments', currentOrgId, params],
        queryFn: async () => {
            if (!currentOrgId) throw new Error('No organization selected');
            const response = await api.get(`/api/v1/organizations/${currentOrgId}/appointments`, {
                params: {
                    date_from: params.date_from,
                    date_to: params.date_to,
                    provider_id: params.provider_id,
                    patient_id: params.patient_id,
                    status: params.status,
                    limit: params.limit || 50,
                    offset: params.offset || 0,
                },
            });
            return response.data;
        },
        enabled: !!currentOrgId,
    });
}

export function useAppointment(appointmentId: string | undefined) {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<Appointment>({
        queryKey: ['appointment', currentOrgId, appointmentId],
        queryFn: async () => {
            if (!currentOrgId) throw new Error('No organization selected');
            const response = await api.get(`/api/v1/organizations/${currentOrgId}/appointments/${appointmentId}`);
            return response.data;
        },
        enabled: !!currentOrgId && !!appointmentId,
    });
}

export function useCreateAppointment() {
    const queryClient = useQueryClient();
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation({
        mutationFn: async (data: AppointmentCreate) => {
            if (!currentOrgId) throw new Error('No organization selected');
            const response = await api.post(`/api/v1/organizations/${currentOrgId}/appointments`, data);
            return response.data as Appointment;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['appointments', currentOrgId] });
        },
    });
}

export function useUpdateAppointmentStatus() {
    const queryClient = useQueryClient();
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation({
        mutationFn: async ({ appointmentId, data }: { appointmentId: string; data: AppointmentStatusUpdate }) => {
            if (!currentOrgId) throw new Error('No organization selected');
            const response = await api.patch(
                `/api/v1/organizations/${currentOrgId}/appointments/${appointmentId}/status`,
                data
            );
            return response.data as Appointment;
        },
        onSuccess: (_, { appointmentId }) => {
            queryClient.invalidateQueries({ queryKey: ['appointments', currentOrgId] });
            queryClient.invalidateQueries({ queryKey: ['appointment', currentOrgId, appointmentId] });
        },
    });
}
