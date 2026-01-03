import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useOrgStore } from "@/store/org-store";

// Types
export interface SubscriptionStatus {
    status: string;
    plan_id: string | null;
    current_period_end: number | null;
    cancel_at_period_end: boolean;
}

export interface CheckoutSessionRequest {
    price_id: string;
}

export interface CheckoutSessionResponse {
    session_id: string;
    checkout_url: string;
}

export interface PortalSessionResponse {
    portal_url: string;
}

// Hooks
export const useSubscription = () => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<SubscriptionStatus>({
        queryKey: ["subscription", currentOrgId],
        queryFn: async () => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.get(`/api/v1/organizations/${currentOrgId}/billing/subscription`);
            return response.data;
        },
        enabled: !!currentOrgId,
    });
};

export const useCreateCheckout = () => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation<CheckoutSessionResponse, Error, CheckoutSessionRequest>({
        mutationFn: async (data) => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.post(`/api/v1/organizations/${currentOrgId}/billing/checkout`, data);
            return response.data;
        },
        onSuccess: (data) => {
            // Redirect to Stripe checkout
            window.location.href = data.checkout_url;
        },
    });
};

export const useBillingPortal = () => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation<PortalSessionResponse, Error, void>({
        mutationFn: async () => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.post(`/api/v1/organizations/${currentOrgId}/billing/portal`);
            return response.data;
        },
        onSuccess: (data) => {
            // Redirect to Stripe portal
            window.location.href = data.portal_url;
        },
    });
};
