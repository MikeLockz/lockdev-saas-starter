import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api as apiClient } from "@/lib/axios";

// =============================================================================
// Types
// =============================================================================

export interface SubscriptionListItem {
  owner_id: string;
  owner_type: string;
  owner_name: string;
  owner_email: string;
  stripe_customer_id: string;
  subscription_status: string;
  plan_id: string | null;
  current_period_end: string | null;
  mrr_cents: number;
  created_at: string;
  cancelled_at: string | null;
  billing_manager_id: string | null;
  billing_manager_name: string | null;
}

export interface SubscriptionListResponse {
  subscriptions: SubscriptionListItem[];
  total: number;
  total_mrr_cents: number;
}

export interface BillingManagerRelationship {
  patient_id: string;
  patient_name: string;
  patient_email: string;
  billing_manager_id: string;
  billing_manager_name: string;
  billing_manager_email: string;
  assigned_at: string;
  assigned_by: string;
  assigned_by_name: string;
}

export interface SubscriptionFilters {
  status?: string;
  owner_type?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface BillingAnalytics {
  total_active_subscriptions: number;
  total_mrr_cents: number;
  new_subscriptions_this_month: number;
  cancelled_subscriptions_this_month: number;
  churn_rate: number;
  average_revenue_per_user_cents: number;
  failed_payments_this_month: number;
  total_revenue_this_month_cents: number;
}

export interface AdminTransaction {
  id: string;
  owner_id: string;
  owner_type: string;
  owner_name: string;
  stripe_payment_intent_id: string;
  stripe_invoice_id: string | null;
  amount_cents: number;
  currency: string;
  status: string;
  description: string | null;
  receipt_url: string | null;
  created_at: string;
  refunded_at: string | null;
  refunded_by: string | null;
  refund_reason: string | null;
}

export interface TransactionListResponse {
  transactions: AdminTransaction[];
  total: number;
  page: number;
  page_size: number;
}

// =============================================================================
// Subscription Queries
// =============================================================================

export function useAdminSubscriptions(filters: SubscriptionFilters = {}) {
  return useQuery({
    queryKey: ["admin-subscriptions", filters],
    queryFn: async () => {
      const params: Record<string, string | number | undefined> = {};
      if (filters.status && filters.status !== "all")
        params.status = filters.status;
      if (filters.owner_type && filters.owner_type !== "all")
        params.owner_type = filters.owner_type;
      if (filters.search) params.search = filters.search;
      if (filters.page) params.page = filters.page;
      if (filters.page_size) params.page_size = filters.page_size;

      const { data } = await apiClient.get<SubscriptionListResponse>(
        "/admin/billing/subscriptions",
        { params },
      );
      return data;
    },
  });
}

// =============================================================================
// Analytics Query
// =============================================================================

export function useBillingAnalytics() {
  return useQuery({
    queryKey: ["billing-analytics"],
    queryFn: async () => {
      const { data } = await apiClient.get<BillingAnalytics>(
        "/admin/billing/analytics",
      );
      return data;
    },
  });
}

// =============================================================================
// Transaction Queries
// =============================================================================

export function useAdminTransactions(page = 1, pageSize = 50, status?: string) {
  return useQuery({
    queryKey: ["admin-transactions", page, pageSize, status],
    queryFn: async () => {
      const params: Record<string, string | number | undefined> = {
        page,
        page_size: pageSize,
      };
      if (status && status !== "all") params.status = status;

      const { data } = await apiClient.get<TransactionListResponse>(
        "/admin/billing/transactions",
        { params },
      );
      return data;
    },
  });
}

// =============================================================================
// Refund Mutation
// =============================================================================

export function useRefundTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      transactionId,
      amountCents,
      reason,
    }: {
      transactionId: string;
      amountCents?: number;
      reason: string;
    }) => {
      const { data } = await apiClient.post(
        `/admin/billing/transactions/${transactionId}/refund`,
        { transaction_id: transactionId, amount_cents: amountCents, reason },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-subscriptions"] });
      queryClient.invalidateQueries({ queryKey: ["admin-transactions"] });
      queryClient.invalidateQueries({ queryKey: ["billing-analytics"] });
    },
  });
}

// =============================================================================
// Grant Free Subscription Mutation
// =============================================================================

export function useGrantFreeSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      ownerId,
      ownerType,
      reason,
      durationMonths,
    }: {
      ownerId: string;
      ownerType: string;
      reason: string;
      durationMonths?: number;
    }) => {
      const { data } = await apiClient.post("/admin/billing/grant-free", {
        owner_id: ownerId,
        owner_type: ownerType,
        reason,
        duration_months: durationMonths,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-subscriptions"] });
    },
  });
}

// =============================================================================
// Cancel Subscription Mutation
// =============================================================================

export function useAdminCancelSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      ownerType,
      ownerId,
      reason,
      cancelImmediately,
    }: {
      ownerType: string;
      ownerId: string;
      reason: string;
      cancelImmediately: boolean;
    }) => {
      const { data } = await apiClient.post(
        `/admin/billing/subscriptions/${ownerType}/${ownerId}/cancel`,
        { reason, cancel_immediately: cancelImmediately },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-subscriptions"] });
      queryClient.invalidateQueries({ queryKey: ["billing-analytics"] });
    },
  });
}

// =============================================================================
// Billing Manager Queries & Mutations
// =============================================================================

export function useBillingManagerRelationships() {
  return useQuery({
    queryKey: ["billing-manager-relationships"],
    queryFn: async () => {
      const { data } = await apiClient.get<BillingManagerRelationship[]>(
        "/admin/billing/managers",
      );
      return data;
    },
  });
}

export function useAdminAssignBillingManager() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      patientId,
      proxyUserId,
    }: {
      patientId: string;
      proxyUserId: string;
    }) => {
      const { data } = await apiClient.put(
        `/admin/patients/${patientId}/billing/manager`,
        { proxy_user_id: proxyUserId },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-subscriptions"] });
      queryClient.invalidateQueries({
        queryKey: ["billing-manager-relationships"],
      });
    },
  });
}

export function useAdminRemoveBillingManager() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (patientId: string) => {
      const { data } = await apiClient.delete(
        `/admin/patients/${patientId}/billing/manager`,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-subscriptions"] });
      queryClient.invalidateQueries({
        queryKey: ["billing-manager-relationships"],
      });
    },
  });
}
