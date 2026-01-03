import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useAuth } from './useAuth';

// Types
export interface MFASetupResponse {
    secret: string;
    provisioning_uri: string;
    qr_code_data_url?: string;
    expires_at: string;
}

export interface MFAVerifyResponse {
    success: boolean;
    mfa_enabled: boolean;
    backup_codes: string[];
    enabled_at: string;
}

export interface MFADisableResponse {
    success: boolean;
    mfa_enabled: boolean;
    disabled_at: string;
}

export function useMFA() {
    const { user } = useAuth();
    const queryClient = useQueryClient();

    const setupMFA = useMutation<MFASetupResponse>({
        mutationFn: async () => {
            const token = await user?.getIdToken();
            const response = await api.post('/api/v1/users/me/mfa/setup', {}, {
                headers: { Authorization: `Bearer ${token}` },
            });
            return response.data;
        },
    });

    const verifyMFA = useMutation<MFAVerifyResponse, Error, { code: string }>({
        mutationFn: async ({ code }) => {
            const token = await user?.getIdToken();
            const response = await api.post('/api/v1/users/me/mfa/verify', { code }, {
                headers: { Authorization: `Bearer ${token}` },
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['userProfile'] });
        },
    });

    const disableMFA = useMutation<MFADisableResponse, Error, { password: string }>({
        mutationFn: async ({ password }) => {
            const token = await user?.getIdToken();
            const response = await api.post('/api/v1/users/me/mfa/disable', { password }, {
                headers: { Authorization: `Bearer ${token}` },
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['userProfile'] });
        },
    });

    return {
        setupMFA,
        verifyMFA,
        disableMFA,
    };
}
