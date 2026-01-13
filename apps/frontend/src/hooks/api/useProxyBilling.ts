import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api as apiClient } from '@/lib/axios';

export interface ManagedPatientSubscription {
    patient_id: string;
    patient_name: string;
    subscription_status: string;
    plan_id: string | null;
    current_period_end: number | null;
    mrr_cents: number;
}

// Get all managed patient subscriptions
export function useManagedPatientSubscriptions() {
    return useQuery({
        queryKey: ['proxy-managed-subscriptions'],
        queryFn: async () => {
            const { data } = await apiClient.get<ManagedPatientSubscription[]>(
                '/proxy/managed-patients/billing'
            );
            return data;
        },
    });
}

// Get specific managed patient subscription
export function useManagedPatientSubscription(patientId: string) {
    return useQuery({
        queryKey: ['proxy-patient-subscription', patientId],
        queryFn: async () => {
            const { data } = await apiClient.get(
                `/proxy/managed-patients/${patientId}/billing/subscription`
            );
            return data;
        },
        enabled: !!patientId,
    });
}

// Create checkout for managed patient
export function useProxyCheckout(patientId: string) {
    return useMutation({
        mutationFn: async (priceId: string) => {
            const { data } = await apiClient.post(
                `/proxy/managed-patients/${patientId}/billing/checkout`,
                { price_id: priceId }
            );
            return data;
        },
        onSuccess: (data) => {
            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            }
        }
    });
}

// Cancel managed patient subscription
export function useProxyCancelSubscription(patientId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({ reason, cancelImmediately }: {
            reason?: string;
            cancelImmediately: boolean;
        }) => {
            const { data } = await apiClient.post(
                `/proxy/managed-patients/${patientId}/billing/cancel`,
                {
                    reason,
                    cancel_immediately: cancelImmediately,
                }
            );
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['proxy-managed-subscriptions'] });
            queryClient.invalidateQueries({ queryKey: ['proxy-patient-subscription', patientId] });
        },
    });
}

// Get managed patient transactions
export function useManagedPatientTransactions(patientId: string, page = 1, pageSize = 20) {
    return useQuery({
        queryKey: ['proxy-patient-transactions', patientId, page, pageSize],
        queryFn: async () => {
            const { data } = await apiClient.get(
                `/proxy/managed-patients/${patientId}/billing/transactions`,
                { params: { page, page_size: pageSize } }
            );
            return data;
        },
        enabled: !!patientId,
    });
}
