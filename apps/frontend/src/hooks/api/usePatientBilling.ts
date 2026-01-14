import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api as apiClient } from "@/lib/axios";

export interface PatientSubscription {
  status: string;
  plan_id: string | null;
  current_period_end: number | null;
  cancel_at_period_end: boolean;
  billing_manager_id?: string | null;
}

export interface BillingTransaction {
  id: string;
  amount_cents: number;
  currency: string;
  status: string;
  description: string | null;
  receipt_url: string | null;
  receipt_number: string | null;
  created_at: string;
  refunded_at: string | null;
  refund_reason: string | null;
}

export interface TransactionListResponse {
  transactions: BillingTransaction[];
  total: number;
  page: number;
  page_size: number;
}

// Get patient subscription
export function usePatientSubscription(patientId: string) {
  return useQuery({
    queryKey: ["patient-subscription", patientId],
    queryFn: async () => {
      const { data } = await apiClient.get<PatientSubscription>(
        `/patients/${patientId}/billing/subscription`,
      );
      return data;
    },
    enabled: !!patientId,
  });
}

// Get patient transactions
export function usePatientTransactions(
  patientId: string,
  page = 1,
  pageSize = 20,
) {
  return useQuery({
    queryKey: ["patient-transactions", patientId, page, pageSize],
    queryFn: async () => {
      const { data } = await apiClient.get<TransactionListResponse>(
        `/patients/${patientId}/billing/transactions`,
        { params: { page, page_size: pageSize } },
      );
      return data;
    },
    enabled: !!patientId,
  });
}

// Create checkout session
export function usePatientCheckout(patientId: string) {
  return useMutation({
    mutationFn: async (priceId: string) => {
      const { data } = await apiClient.post(
        `/patients/${patientId}/billing/checkout`,
        { price_id: priceId },
      );
      return data;
    },
    onSuccess: (data) => {
      // Redirect to checkout
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    },
  });
}

// Create billing portal session
export function usePatientBillingPortal(patientId: string) {
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post(
        `/patients/${patientId}/billing/portal`,
      );
      return data;
    },
    onSuccess: (data) => {
      // Redirect to portal
      if (data.portal_url) {
        window.location.href = data.portal_url;
      }
    },
  });
}

// Cancel subscription
export function useCancelPatientSubscription(patientId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      reason,
      cancelImmediately,
    }: {
      reason?: string;
      cancelImmediately: boolean;
    }) => {
      const { data } = await apiClient.post(
        `/patients/${patientId}/billing/cancel`,
        {
          reason,
          cancel_immediately: cancelImmediately,
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["patient-subscription", patientId],
      });
    },
  });
}

// Assign billing manager
export function useAssignBillingManager(patientId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (proxyUserId: string) => {
      const { data } = await apiClient.put(
        `/patients/${patientId}/billing/manager`,
        { proxy_user_id: proxyUserId },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["patient-subscription", patientId],
      });
    },
  });
}

// Remove billing manager
export function useRemoveBillingManager(patientId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.delete(
        `/patients/${patientId}/billing/manager`,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["patient-subscription", patientId],
      });
    },
  });
}
