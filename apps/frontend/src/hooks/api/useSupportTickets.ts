import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/axios';

export interface SupportMessage {
    id: string;
    ticket_id: string;
    sender_id: string;
    body: string;
    is_internal: boolean;
    created_at: string;
}

export interface SupportTicket {
    id: string;
    user_id: string;
    organization_id?: string;
    subject: string;
    category: string;
    priority: string;
    status: string;
    assigned_to_id?: string;
    created_at: string;
    updated_at: string;
    resolved_at?: string;
    message_count: number;
    messages: SupportMessage[];
}

export interface CreateTicketRequest {
    subject: string;
    category: string;
    priority: string;
    initial_message: string;
}

export interface AddMessageRequest {
    body: string;
    is_internal?: boolean;
}

export function useSupportTickets() {
    return useQuery<SupportTicket[]>({
        queryKey: ['support', 'tickets'],
        queryFn: async () => {
            const response = await api.get('/api/v1/support/tickets');
            return response.data;
        },
    });
}

export function useSupportTicket(ticketId: string) {
    return useQuery<SupportTicket>({
        queryKey: ['support', 'tickets', ticketId],
        queryFn: async () => {
            const response = await api.get(`/api/v1/support/tickets/${ticketId}`);
            return response.data;
        },
        enabled: !!ticketId,
    });
}

export function useCreateTicket() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (data: CreateTicketRequest) => {
            const response = await api.post('/api/v1/support/tickets', data);
            return response.data as SupportTicket;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['support', 'tickets'] });
        },
    });
}

export function useAddMessage(ticketId: string) {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (data: AddMessageRequest) => {
            const response = await api.post(`/api/v1/support/tickets/${ticketId}/messages`, data);
            return response.data as SupportMessage;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['support', 'tickets', ticketId] });
        },
    });
}

// Admin hooks
export function useAdminTickets(params?: { status?: string; assigned_to_me?: boolean }) {
    return useQuery<SupportTicket[]>({
        queryKey: ['support', 'admin', 'tickets', params],
        queryFn: async () => {
            const response = await api.get('/api/v1/support/admin/tickets', { params });
            return response.data;
        },
    });
}

export function useUpdateTicketStatus(ticketId: string) {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (data: { status?: string; priority?: string; assigned_to_id?: string }) => {
            const response = await api.patch(`/api/v1/support/admin/tickets/${ticketId}`, data);
            return response.data as SupportTicket;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['support'] });
        },
    });
}
