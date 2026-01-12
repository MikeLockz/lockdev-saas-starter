# Story 22.3: Patient & Proxy Billing Frontend
**User Story:** As a Patient or Proxy (Billing Manager), I want user-friendly billing interfaces to manage subscriptions, view payment history, download receipts, and manage multiple patient accounts.

## Status
- [ ] **Pending**

## Context
- **Epic:** Epic 22 - Complete Billing & Subscription Management
- **Dependencies:**
  - Story 22.1 (Patient Billing API) - includes proxy billing endpoints
  - Story 22.2 (Email & Receipts)
- **Existing Code:**
  - `frontend/src/hooks/api/useBilling.ts` - Billing hooks (org-level)
  - `frontend/src/components/billing/` - Billing components
  - `frontend/src/routes/_auth/admin/billing.tsx` - Admin billing page

## Proxy Billing UI Requirements
**Key Features:** Proxy billing management dashboard and patient billing manager assignment.

### Patient Features
- Patient can view/manage own subscription
- Patient can assign/remove billing manager from UI
- Patient can see who their billing manager is
- UI clearly indicates when billing is proxy-managed

### Proxy Features
- Proxy dashboard showing all managed patient subscriptions
- Quick overview of billing status for each patient
- Ability to manage billing for any assigned patient
- Access controls ensure proxy only sees assigned patients

## Technical Specification
**Goal:** Build patient and proxy billing UIs with subscription management, transaction history, and billing manager assignment.

### Changes Required

#### 1. API Hooks: `frontend/src/hooks/api/usePatientBilling.ts` (NEW)
```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface PatientSubscription {
  status: string;
  plan_id: string | null;
  current_period_end: number | null;
  cancel_at_period_end: boolean;
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
    queryKey: ['patient-subscription', patientId],
    queryFn: async () => {
      const { data } = await apiClient.get<PatientSubscription>(
        `/patients/${patientId}/billing/subscription`
      );
      return data;
    },
    enabled: !!patientId,
  });
}

// Get patient transactions
export function usePatientTransactions(patientId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['patient-transactions', patientId, page, pageSize],
    queryFn: async () => {
      const { data } = await apiClient.get<TransactionListResponse>(
        `/patients/${patientId}/billing/transactions`,
        { params: { page, page_size: pageSize } }
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
        { price_id: priceId }
      );
      // Redirect to checkout
      window.location.href = data.checkout_url;
      return data;
    },
  });
}

// Create billing portal session
export function usePatientBillingPortal(patientId: string) {
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post(
        `/patients/${patientId}/billing/portal`
      );
      // Redirect to portal
      window.location.href = data.portal_url;
      return data;
    },
  });
}

// Cancel subscription
export function useCancelPatientSubscription(patientId: string) {
  return useMutation({
    mutationFn: async ({ reason, cancelImmediately }: {
      reason?: string;
      cancelImmediately: boolean;
    }) => {
      const { data } = await apiClient.post(
        `/patients/${patientId}/billing/cancel`,
        {
          reason,
          cancel_immediately: cancelImmediately,
        }
      );
      return data;
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
        { proxy_user_id: proxyUserId }
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patient-subscription', patientId] });
    },
  });
}

// Remove billing manager
export function useRemoveBillingManager(patientId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.delete(
        `/patients/${patientId}/billing/manager`
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patient-subscription', patientId] });
    },
  });
}
```

#### 2. Proxy Billing Hooks: `frontend/src/hooks/api/useProxyBilling.ts` (NEW)
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export interface ManagedPatientSubscription {
  patient_id: string;
  patient_name: string;
  subscription_status: string;
  plan_id: string | null;
  current_period_end: string | null;
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
      window.location.href = data.checkout_url;
      return data;
    },
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
```

#### 2. Patient Billing Page: `frontend/src/routes/_auth/patient/billing.tsx` (NEW)
```typescript
import { createFileRoute } from '@tanstack/react-router';
import { PatientSubscriptionCard } from '@/components/billing/PatientSubscriptionCard';
import { PatientPlanSelector } from '@/components/billing/PatientPlanSelector';
import { TransactionHistory } from '@/components/billing/TransactionHistory';
import { usePatientSubscription } from '@/hooks/api/usePatientBilling';
import { useCurrentPatient } from '@/hooks/useCurrentPatient';

export const Route = createFileRoute('/_auth/patient/billing')({
  component: PatientBillingPage,
});

function PatientBillingPage() {
  const { currentPatient } = useCurrentPatient();
  const { data: subscription, isLoading } = usePatientSubscription(currentPatient?.id || '');

  if (isLoading) {
    return <div>Loading billing information...</div>;
  }

  const hasActiveSubscription = subscription?.status === 'ACTIVE' || subscription?.status === 'TRIALING';

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">My Billing</h1>

      {/* Current Subscription Status */}
      <div className="mb-8">
        <PatientSubscriptionCard
          subscription={subscription}
          patientId={currentPatient?.id || ''}
        />
      </div>

      {/* Billing Manager Assignment (if has proxies) */}
      <div className="mb-8">
        <BillingManagerAssignment
          patientId={currentPatient?.id || ''}
          currentBillingManagerId={subscription?.billing_manager_id}
        />
      </div>

      {/* Plan Selection (if no subscription) */}
      {!hasActiveSubscription && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Choose a Plan</h2>
          <PatientPlanSelector patientId={currentPatient?.id || ''} />
        </div>
      )}

      {/* Transaction History */}
      {hasActiveSubscription && (
        <div>
          <h2 className="text-2xl font-semibold mb-4">Payment History</h2>
          <TransactionHistory patientId={currentPatient?.id || ''} />
        </div>
      )}
    </div>
  );
}
```

#### 3. Proxy Billing Dashboard: `frontend/src/routes/_auth/proxy/managed-patients-billing.tsx` (NEW)
```typescript
import { createFileRoute, Link } from '@tanstack/react-router';
import { useManagedPatientSubscriptions } from '@/hooks/api/useProxyBilling';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatDate, formatCurrency } from '@/lib/utils';

export const Route = createFileRoute('/_auth/proxy/managed-patients-billing')({
  component: ProxyManagedPatientsBilling,
});

function ProxyManagedPatientsBilling() {
  const { data: subscriptions, isLoading } = useManagedPatientSubscriptions();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'success' | 'warning' | 'destructive' | 'default'> = {
      ACTIVE: 'success',
      TRIALING: 'default',
      PAST_DUE: 'warning',
      CANCELED: 'destructive',
      NONE: 'outline',
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Managed Patient Billing</h1>
        <p className="text-muted-foreground mt-2">
          You are managing billing for {subscriptions?.length || 0} patient(s)
        </p>
      </div>

      {subscriptions && subscriptions.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">
              You are not currently managing billing for any patients.
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Patients can assign you as their billing manager from their billing page.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {subscriptions?.map((sub) => (
            <Card key={sub.patient_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{sub.patient_name}</CardTitle>
                    <CardDescription className="mt-2">
                      {getStatusBadge(sub.subscription_status)}
                    </CardDescription>
                  </div>
                  <Button asChild>
                    <Link to={`/proxy/managed-patients/${sub.patient_id}/billing`}>
                      Manage Billing
                    </Link>
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Plan</p>
                    <p className="font-medium">{sub.plan_id || 'No active plan'}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">MRR</p>
                    <p className="font-medium">{formatCurrency(sub.mrr_cents / 100)}</p>
                  </div>
                  {sub.current_period_end && (
                    <div className="col-span-2">
                      <p className="text-muted-foreground">Next billing date</p>
                      <p className="font-medium">
                        {formatDate(new Date(sub.current_period_end))}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
```

#### 4. Billing Manager Assignment: `frontend/src/components/billing/BillingManagerAssignment.tsx` (NEW)
```typescript
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { useAssignBillingManager, useRemoveBillingManager } from '@/hooks/api/usePatientBilling';
import { usePatientProxies } from '@/hooks/api/useProxies';
import { toast } from 'sonner';
import { User, UserMinus } from 'lucide-react';

interface Props {
  patientId: string;
  currentBillingManagerId?: string;
}

export function BillingManagerAssignment({ patientId, currentBillingManagerId }: Props) {
  const { data: proxies } = usePatientProxies(patientId);
  const assignMutation = useAssignBillingManager(patientId);
  const removeMutation = useRemoveBillingManager(patientId);
  const [selectedProxyId, setSelectedProxyId] = useState<string | undefined>(currentBillingManagerId);

  const activeProxies = proxies?.filter(p => p.status === 'ACTIVE') || [];
  const currentManager = activeProxies.find(p => p.proxy_user_id === currentBillingManagerId);

  const handleAssign = async () => {
    if (!selectedProxyId) return;

    try {
      await assignMutation.mutateAsync(selectedProxyId);
      toast.success('Billing manager assigned successfully');
    } catch (error) {
      toast.error('Failed to assign billing manager');
    }
  };

  const handleRemove = async () => {
    try {
      await removeMutation.mutateAsync();
      setSelectedProxyId(undefined);
      toast.success('Billing manager removed successfully');
    } catch (error) {
      toast.error('Failed to remove billing manager');
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <User className="h-5 w-5" />
          <CardTitle>Billing Manager</CardTitle>
        </div>
        <CardDescription>
          Assign a proxy to manage billing on your behalf. They will receive all billing emails and can manage your subscription.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {currentManager ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div>
                <p className="font-medium">{currentManager.proxy_name}</p>
                <p className="text-sm text-muted-foreground">{currentManager.proxy_email}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Currently managing your billing
                </p>
              </div>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <UserMinus className="h-4 w-4 mr-2" />
                    Remove
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Remove Billing Manager?</AlertDialogTitle>
                    <AlertDialogDescription>
                      {currentManager.proxy_name} will no longer be able to manage your billing.
                      You will receive all billing emails directly. You can reassign them later if needed.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleRemove}>
                      Remove Billing Manager
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        ) : activeProxies.length > 0 ? (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Select a proxy to manage your billing
              </label>
              <Select value={selectedProxyId} onValueChange={setSelectedProxyId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a proxy..." />
                </SelectTrigger>
                <SelectContent>
                  {activeProxies.map((proxy) => (
                    <SelectItem key={proxy.proxy_user_id} value={proxy.proxy_user_id}>
                      {proxy.proxy_name} ({proxy.proxy_email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={handleAssign}
              disabled={!selectedProxyId || assignMutation.isPending}
            >
              Assign Billing Manager
            </Button>
          </div>
        ) : (
          <div className="text-center py-4">
            <p className="text-muted-foreground text-sm">
              You don't have any active proxies. Add a proxy first to assign them as billing manager.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

#### 3. Patient Subscription Card: `frontend/src/components/billing/PatientSubscriptionCard.tsx` (NEW)
```typescript
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { usePatientBillingPortal, useCancelPatientSubscription, type PatientSubscription } from '@/hooks/api/usePatientBilling';
import { formatDate } from '@/lib/utils';
import { CreditCard, AlertCircle } from 'lucide-react';

interface Props {
  subscription: PatientSubscription | undefined;
  patientId: string;
}

export function PatientSubscriptionCard({ subscription, patientId }: Props) {
  const portalMutation = usePatientBillingPortal(patientId);
  const cancelMutation = useCancelPatientSubscription(patientId);

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'success' | 'warning' | 'destructive' | 'default'> = {
      ACTIVE: 'success',
      TRIALING: 'default',
      PAST_DUE: 'warning',
      CANCELED: 'destructive',
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  if (!subscription || subscription.status === 'NONE') {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Active Subscription</CardTitle>
          <CardDescription>
            You don't have an active subscription yet. Choose a plan below to get started.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Current Subscription
            </CardTitle>
            <CardDescription className="mt-2">
              Manage your subscription and payment methods
            </CardDescription>
          </div>
          {getStatusBadge(subscription.status)}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Plan</p>
            <p className="text-lg font-semibold">{subscription.plan_id || 'Unknown'}</p>
          </div>
          {subscription.current_period_end && (
            <div>
              <p className="text-sm text-muted-foreground">
                {subscription.cancel_at_period_end ? 'Cancels on' : 'Next billing date'}
              </p>
              <p className="text-lg font-semibold">
                {formatDate(new Date(subscription.current_period_end * 1000))}
              </p>
            </div>
          )}
        </div>

        {subscription.cancel_at_period_end && (
          <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <AlertCircle className="h-5 w-5 text-yellow-600" />
            <p className="text-sm text-yellow-800">
              Your subscription will be cancelled at the end of the current billing period.
            </p>
          </div>
        )}

        <div className="flex gap-3">
          <Button
            onClick={() => portalMutation.mutate()}
            disabled={portalMutation.isPending}
          >
            Manage Payment Method
          </Button>

          {!subscription.cancel_at_period_end && (
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline">Cancel Subscription</Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Cancel Subscription?</AlertDialogTitle>
                  <AlertDialogDescription>
                    You can cancel your subscription immediately or at the end of your current billing period.
                    If you cancel now, you'll lose access immediately. If you cancel at period end,
                    you'll retain access until {formatDate(new Date(subscription.current_period_end! * 1000))}.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Keep Subscription</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={() => cancelMutation.mutate({ cancelImmediately: false })}
                  >
                    Cancel at Period End
                  </AlertDialogAction>
                  <AlertDialogAction
                    variant="destructive"
                    onClick={() => cancelMutation.mutate({ cancelImmediately: true })}
                  >
                    Cancel Immediately
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

#### 4. Patient Plan Selector: `frontend/src/components/billing/PatientPlanSelector.tsx` (NEW)
```typescript
// Similar to existing PlanSelector but uses patient-specific hooks
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Check } from 'lucide-react';
import { usePatientCheckout } from '@/hooks/api/usePatientBilling';

const PLANS = [
  {
    id: 'price_starter',
    name: 'Starter',
    price: 29,
    features: [
      'Basic scheduling',
      'Email reminders',
      '5GB document storage',
      'Email support',
    ],
  },
  {
    id: 'price_professional',
    name: 'Professional',
    price: 79,
    popular: true,
    features: [
      'Everything in Starter',
      'Advanced scheduling',
      '25GB document storage',
      'Priority support',
      'Care team access',
    ],
  },
  {
    id: 'price_enterprise',
    name: 'Enterprise',
    price: 199,
    features: [
      'Everything in Professional',
      'Unlimited storage',
      '24/7 phone support',
      'Custom integrations',
      'Dedicated account manager',
    ],
  },
];

interface Props {
  patientId: string;
}

export function PatientPlanSelector({ patientId }: Props) {
  const checkoutMutation = usePatientCheckout(patientId);

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {PLANS.map((plan) => (
        <Card
          key={plan.id}
          className={plan.popular ? 'border-primary shadow-lg' : ''}
        >
          <CardHeader>
            {plan.popular && (
              <Badge className="w-fit mb-2">Most Popular</Badge>
            )}
            <CardTitle>{plan.name}</CardTitle>
            <CardDescription>
              <span className="text-3xl font-bold text-foreground">
                ${plan.price}
              </span>
              /month
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <ul className="space-y-2">
              {plan.features.map((feature, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" />
                  <span className="text-sm">{feature}</span>
                </li>
              ))}
            </ul>
            <Button
              className="w-full"
              onClick={() => checkoutMutation.mutate(plan.id)}
              disabled={checkoutMutation.isPending}
            >
              {checkoutMutation.isPending ? 'Loading...' : 'Get Started'}
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

#### 5. Transaction History: `frontend/src/components/billing/TransactionHistory.tsx` (NEW)
```typescript
import { useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { usePatientTransactions } from '@/hooks/api/usePatientBilling';
import { formatDate, formatCurrency } from '@/lib/utils';
import { Download, ChevronLeft, ChevronRight } from 'lucide-react';

interface Props {
  patientId: string;
}

export function TransactionHistory({ patientId }: Props) {
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const { data, isLoading } = usePatientTransactions(patientId, page, pageSize);

  if (isLoading) {
    return <div>Loading transactions...</div>;
  }

  if (!data || data.transactions.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No payment history yet.
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / pageSize);

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'success' | 'warning' | 'destructive' | 'default'> = {
      SUCCEEDED: 'success',
      PENDING: 'warning',
      FAILED: 'destructive',
      REFUNDED: 'default',
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Receipt</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.transactions.map((transaction) => (
            <TableRow key={transaction.id}>
              <TableCell>
                {formatDate(new Date(transaction.created_at))}
              </TableCell>
              <TableCell>{transaction.description || 'Subscription payment'}</TableCell>
              <TableCell className="font-semibold">
                {formatCurrency(transaction.amount_cents / 100, transaction.currency)}
              </TableCell>
              <TableCell>{getStatusBadge(transaction.status)}</TableCell>
              <TableCell>
                {transaction.receipt_url ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    asChild
                  >
                    <a
                      href={transaction.receipt_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </a>
                  </Button>
                ) : (
                  <span className="text-muted-foreground text-sm">N/A</span>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, data.total)} of {data.total} transactions
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 6. Success/Cancel Pages: `frontend/src/routes/_auth/patient/billing-success.tsx` (NEW)
```typescript
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useEffect } from 'react';
import { CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const Route = createFileRoute('/_auth/patient/billing-success')({
  component: BillingSuccessPage,
});

function BillingSuccessPage() {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <div className="text-center space-y-6">
        <CheckCircle className="h-16 w-16 text-green-600 mx-auto" />
        <h1 className="text-3xl font-bold">Payment Successful!</h1>
        <p className="text-muted-foreground">
          Your subscription has been activated. You'll receive a confirmation email shortly with your receipt.
        </p>
        <Button
          onClick={() => navigate({ to: '/patient/billing' })}
        >
          View Billing Dashboard
        </Button>
      </div>
    </div>
  );
}
```

#### 7. Route Configuration: `frontend/src/routes/_auth/patient.tsx` (EXTEND)
```typescript
// Add billing routes to patient layout
```

## Acceptance Criteria
### Patient Billing UI
- [ ] Patient billing page displays current subscription status.
- [ ] Patients can select and subscribe to a plan.
- [ ] Redirect to Stripe checkout works correctly.
- [ ] Success/cancel pages display after checkout.
- [ ] Transaction history loads with pagination.
- [ ] Receipt download links work.
- [ ] Subscription cancellation dialog works (immediate vs end of period).
- [ ] Billing portal link redirects to Stripe portal.

### Billing Manager Assignment UI
- [ ] Billing manager assignment card displays on patient billing page.
- [ ] Patient can see current billing manager if assigned.
- [ ] Patient can select from list of active proxies.
- [ ] Patient can assign billing manager with confirmation.
- [ ] Patient can remove billing manager with confirmation dialog.
- [ ] UI shows empty state when no active proxies exist.
- [ ] Assignment/removal success messages display.

### Proxy Billing Dashboard
- [ ] Proxy dashboard displays all managed patient subscriptions.
- [ ] Dashboard shows patient name, status, plan, and MRR for each.
- [ ] Proxy can click "Manage Billing" to access patient billing page.
- [ ] Dashboard shows empty state when no patients managed.
- [ ] Patient count displayed correctly in header.
- [ ] Status badges display with correct colors.

### Proxy Patient Billing Page
- [ ] Proxy can view individual patient subscription details.
- [ ] Proxy can create checkout for patient.
- [ ] Proxy can cancel patient subscription.
- [ ] Proxy can view patient transaction history.
- [ ] UI clearly indicates proxy is managing on behalf of patient.
- [ ] Access denied if proxy not assigned as billing manager.

### General UI Requirements
- [ ] All pages responsive on mobile devices.
- [ ] Loading and error states handled gracefully.
- [ ] Toasts/notifications display for all actions.
- [ ] Form validation works correctly.
- [ ] Keyboard navigation supported.

## Verification Plan
**Automated Tests:**
```bash
pnpm test src/components/billing --run
pnpm exec playwright test e2e/patient-billing.spec.ts
```

**Manual Verification:**
1. Navigate to patient billing page
2. Select a plan and complete checkout
3. Verify redirect to success page
4. Check transaction appears in history
5. Download a receipt PDF
6. Cancel subscription (both options)
7. Update payment method via portal
8. Test on mobile browser

## Accessibility
- [ ] All interactive elements keyboard accessible
- [ ] ARIA labels on all buttons and links
- [ ] Screen reader announcements for status changes
- [ ] Focus management in dialogs
- [ ] Color contrast meets WCAG AA standards
- [ ] Error messages clearly communicated

## Rollback Plan
If issues arise:
1. Hide patient billing route via feature flag
2. Continue using org-level billing only
3. Fix UI issues in staging
4. Gradually roll out to user segments
