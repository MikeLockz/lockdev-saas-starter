import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useAuth } from './useAuth';

// Types
export interface CommunicationPreferences {
    transactional_consent: boolean;
    marketing_consent: boolean;
    updated_at: string;
}

export interface PreferencesUpdate {
    transactional_consent?: boolean;
    marketing_consent?: boolean;
}

export function usePreferences() {
    const { user } = useAuth();
    const queryClient = useQueryClient();

    const { data: preferences, isLoading, error } = useQuery<CommunicationPreferences>({
        queryKey: ['communicationPreferences'],
        queryFn: async () => {
            const token = await user?.getIdToken();
            const response = await api.get('/api/v1/users/me/communication-preferences', {
                headers: { Authorization: `Bearer ${token}` },
            });
            return response.data;
        },
        enabled: !!user,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });

    const updatePreferences = useMutation({
        mutationFn: async (data: PreferencesUpdate) => {
            const token = await user?.getIdToken();
            const response = await api.patch('/api/v1/users/me/communication-preferences', data, {
                headers: { Authorization: `Bearer ${token}` },
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['communicationPreferences'] });
        },
    });

    return {
        preferences,
        isLoading,
        error,
        updatePreferences,
    };
}
