import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/axios';

export interface AuditLog {
    id: string;
    actor_user_id?: string;
    organization_id?: string;
    resource_type: string;
    resource_id: string;
    action_type: string;
    ip_address?: string;
    user_agent?: string;
    impersonator_id?: string;
    changes_json?: Record<string, unknown>;
    occurred_at: string;
}

export interface AuditLogListResponse {
    items: AuditLog[];
    total: number;
    page: number;
    page_size: number;
}

export interface AuditLogSearchParams {
    action_type?: string;
    resource_type?: string;
    resource_id?: string;
    actor_user_id?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    page_size?: number;
}

export function useAuditLogs(params: AuditLogSearchParams = {}) {
    return useQuery<AuditLogListResponse>({
        queryKey: ['admin', 'audit-logs', params],
        queryFn: async () => {
            const response = await api.get('/api/v1/admin/audit-logs', { params });
            return response.data;
        },
    });
}

export function useAuditLog(logId: string) {
    return useQuery<AuditLog>({
        queryKey: ['admin', 'audit-logs', logId],
        queryFn: async () => {
            const response = await api.get(`/api/v1/admin/audit-logs/${logId}`);
            return response.data;
        },
        enabled: !!logId,
    });
}

export function exportAuditLogs(params: AuditLogSearchParams = {}) {
    return api.get('/api/v1/admin/audit-logs/export', {
        params,
        responseType: 'blob'
    });
}
