import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/axios';

export interface OrganizationAdmin {
    id: string;
    name: string;
    member_count: number;
    patient_count: number;
    subscription_status: string;
    is_active: boolean;
    created_at: string;
}

export interface OrganizationListResponse {
    items: OrganizationAdmin[];
    total: number;
    page: number;
    page_size: number;
}

export interface UserAdmin {
    id: string;
    email: string;
    display_name?: string;
    is_super_admin: boolean;
    locked_until?: string;
    failed_login_attempts: number;
    last_login_at?: string;
    created_at: string;
}

export interface UserListResponse {
    items: UserAdmin[];
    total: number;
    page: number;
    page_size: number;
}

export interface SystemHealth {
    db_status: string;
    redis_status: string;
    worker_status: string;
    metrics: {
        total_users: number;
        total_organizations: number;
    };
}

export interface OrganizationSearchParams {
    search?: string;
    page?: number;
    page_size?: number;
}

export interface UserSearchParams {
    search?: string;
    is_locked?: boolean;
    is_super_admin?: boolean;
    page?: number;
    page_size?: number;
}

export function useSuperAdminOrganizations(params: OrganizationSearchParams = {}) {
    return useQuery<OrganizationListResponse>({
        queryKey: ['super-admin', 'organizations', params],
        queryFn: async () => {
            const response = await api.get('/api/v1/admin/super-admin/organizations', { params });
            return response.data;
        },
    });
}

export function useSuperAdminOrganization(orgId: string) {
    return useQuery<OrganizationAdmin>({
        queryKey: ['super-admin', 'organizations', orgId],
        queryFn: async () => {
            const response = await api.get(`/api/v1/admin/super-admin/organizations/${orgId}`);
            return response.data;
        },
        enabled: !!orgId,
    });
}

export function useUpdateOrganization() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ orgId, data }: { orgId: string; data: { is_active?: boolean; subscription_status?: string } }) => {
            const response = await api.patch(`/api/v1/admin/super-admin/organizations/${orgId}`, data);
            return response.data as OrganizationAdmin;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['super-admin', 'organizations'] });
        },
    });
}

export function useSuperAdminUsers(params: UserSearchParams = {}) {
    return useQuery<UserListResponse>({
        queryKey: ['super-admin', 'users', params],
        queryFn: async () => {
            const response = await api.get('/api/v1/admin/super-admin/users', { params });
            return response.data;
        },
    });
}

export function useUnlockUser() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (userId: string) => {
            const response = await api.patch(`/api/v1/admin/super-admin/users/${userId}/unlock`);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['super-admin', 'users'] });
        },
    });
}

export function useUpdateUserAdmin() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ userId, data }: { userId: string; data: { is_super_admin?: boolean } }) => {
            const response = await api.patch(`/api/v1/admin/super-admin/users/${userId}`, data);
            return response.data as UserAdmin;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['super-admin', 'users'] });
        },
    });
}

export function useSystemHealth() {
    return useQuery<SystemHealth>({
        queryKey: ['super-admin', 'system'],
        queryFn: async () => {
            const response = await api.get('/api/v1/admin/super-admin/system');
            return response.data;
        },
        refetchInterval: 30000, // Refresh every 30 seconds
    });
}
