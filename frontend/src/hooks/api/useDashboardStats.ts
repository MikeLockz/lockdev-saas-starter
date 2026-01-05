import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useOrgStore } from '@/store/org-store';

// Re-export useUnreadCount for notification count
export { useUnreadCount } from './useNotifications';

// Types
interface ThreadListResponse {
    items: Array<{
        id: string;
        unread_count: number;
    }>;
    total: number;
}

/**
 * Get count of today's appointments for the current organization.
 * Returns SCHEDULED and CONFIRMED appointments only.
 */
export function useTodaysAppointmentsCount() {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<number>({
        queryKey: ['dashboard', 'appointments-today', currentOrgId],
        queryFn: async () => {
            if (!currentOrgId) return 0;

            // Get today's date range in ISO format
            const today = new Date();
            const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
            const endOfDay = new Date(startOfDay.getTime() + 24 * 60 * 60 * 1000);

            const response = await api.get(`/api/v1/organizations/${currentOrgId}/appointments`, {
                params: {
                    date_from: startOfDay.toISOString(),
                    date_to: endOfDay.toISOString(),
                    limit: 100,
                },
            });

            // Filter to only SCHEDULED and CONFIRMED appointments
            const appointments = response.data as Array<{ status: string }>;
            const activeAppointments = appointments.filter(
                (a) => a.status === 'SCHEDULED' || a.status === 'CONFIRMED'
            );
            return activeAppointments.length;
        },
        enabled: !!currentOrgId,
        staleTime: 60000, // Cache for 1 minute
    });
}

/**
 * Get total count of unread messages across all threads for the current user.
 */
export function useUnreadMessagesCount() {
    return useQuery<number>({
        queryKey: ['dashboard', 'unread-messages'],
        queryFn: async () => {
            const response = await api.get<ThreadListResponse>('/api/v1/messages', {
                params: { page: 1, size: 100 },
            });

            // Sum unread_count across all threads
            const totalUnread = response.data.items.reduce(
                (sum, thread) => sum + (thread.unread_count || 0),
                0
            );
            return totalUnread;
        },
        staleTime: 30000, // Cache for 30 seconds
    });
}

interface SessionListResponse {
    items: unknown[];
    total: number;
}

/**
 * Get count of active sessions for the current user.
 */
export function useActiveSessionsCount() {
    return useQuery<number>({
        queryKey: ['dashboard', 'active-sessions'],
        queryFn: async () => {
            const response = await api.get<SessionListResponse>('/api/v1/users/me/sessions');
            return response.data.total;
        },
        staleTime: 60000, // Cache for 1 minute
    });
}

// Types for provider dashboard
export interface ProviderAppointment {
    id: string;
    patient_id: string;
    scheduled_at: string;
    duration_minutes: number;
    appointment_type: string;
    reason: string | null;
    status: string;
    patient_name?: string;
}

export interface ProviderTask {
    id: string;
    title: string;
    status: string;
    priority: string;
    due_date: string | null;
    patient_name?: string;
}

/**
 * Get today's appointments for a specific provider.
 * Used in the Provider Overview Card.
 */
export function useProviderTodaysAppointments(providerId: string | undefined) {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<ProviderAppointment[]>({
        queryKey: ['dashboard', 'provider-appointments-today', currentOrgId, providerId],
        queryFn: async () => {
            if (!currentOrgId || !providerId) return [];

            // Get today's date range in ISO format
            const today = new Date();
            const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
            const endOfDay = new Date(startOfDay.getTime() + 24 * 60 * 60 * 1000);

            const response = await api.get(`/api/v1/organizations/${currentOrgId}/appointments`, {
                params: {
                    provider_id: providerId,
                    date_from: startOfDay.toISOString(),
                    date_to: endOfDay.toISOString(),
                    limit: 20,
                },
            });

            // Filter to only SCHEDULED and CONFIRMED appointments, sorted by time
            const appointments = response.data as ProviderAppointment[];
            return appointments
                .filter((a) => a.status === 'SCHEDULED' || a.status === 'CONFIRMED')
                .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());
        },
        enabled: !!currentOrgId && !!providerId,
        staleTime: 60000, // Cache for 1 minute
    });
}

/**
 * Get pending tasks for a specific assignee (provider).
 * Used in the Provider Overview Card.
 */
export function useProviderPendingTasks(assigneeId: string | undefined) {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<ProviderTask[]>({
        queryKey: ['dashboard', 'provider-pending-tasks', currentOrgId, assigneeId],
        queryFn: async () => {
            if (!currentOrgId || !assigneeId) return [];

            const response = await api.get(`/api/v1/organizations/${currentOrgId}/tasks`, {
                params: {
                    assignee_id: assigneeId,
                    limit: 50,
                },
            });

            // Filter to only TODO and IN_PROGRESS tasks
            const tasks = response.data as ProviderTask[];
            return tasks.filter((t) => t.status === 'TODO' || t.status === 'IN_PROGRESS');
        },
        enabled: !!currentOrgId && !!assigneeId,
        staleTime: 60000, // Cache for 1 minute
    });
}

// Types for patient dashboard
export interface PatientAppointment {
    id: string;
    provider_id: string;
    scheduled_at: string;
    duration_minutes: number;
    appointment_type: string;
    reason: string | null;
    status: string;
    provider_name?: string;
}

/**
 * Get upcoming appointments for a specific patient.
 * Used in the Patient Overview Card.
 */
export function usePatientUpcomingAppointments(patientId: string | undefined) {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<PatientAppointment[]>({
        queryKey: ['dashboard', 'patient-upcoming-appointments', currentOrgId, patientId],
        queryFn: async () => {
            if (!currentOrgId || !patientId) return [];

            // Get appointments from now onwards
            const now = new Date();

            const response = await api.get(`/api/v1/organizations/${currentOrgId}/appointments`, {
                params: {
                    patient_id: patientId,
                    date_from: now.toISOString(),
                    limit: 10,
                },
            });

            // Filter to only SCHEDULED and CONFIRMED appointments, sorted by date
            const appointments = response.data as PatientAppointment[];
            return appointments
                .filter((a) => a.status === 'SCHEDULED' || a.status === 'CONFIRMED')
                .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())
                .slice(0, 3); // Return next 3
        },
        enabled: !!currentOrgId && !!patientId,
        staleTime: 60000, // Cache for 1 minute
    });
}

