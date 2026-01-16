# Story 22.5: Admin Billing Management Frontend
**User Story:** As an Admin, I want a comprehensive billing dashboard to manage all subscriptions, issue refunds, view payment analytics, and manage billing manager assignments.

## Status
- [x] **Complete**

## Context
- **Epic:** Epic 22 - Complete Billing & Subscription Management
- **Dependencies:**
  - Story 22.4 (Admin Billing API)
- **Existing Code:**
  - `frontend/src/routes/_auth/admin/` - Admin pages
  - `frontend/src/components/ui/` - UI components

## Billing Manager Management Requirements
**Key Feature:** Admins can view, assign, and remove billing managers from the admin dashboard.

- View all billing manager relationships in a dedicated tab
- Show billing manager info in subscriptions table
- Assign billing manager from subscription actions menu
- Remove billing manager from subscription actions menu
- Search and filter billing manager relationships

## Technical Specification
**Goal:** Build admin UI for comprehensive billing management with search, filters, and bulk actions.

### Changes Required

#### 1. API Hooks: `frontend/src/hooks/api/useAdminBilling.ts` (NEW)
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

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
  billing_manager_id: string | null;  // NEW
  billing_manager_name: string | null;  // NEW
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

// List all subscriptions
export function useAdminSubscriptions(filters: SubscriptionFilters) {
  return useQuery({
    queryKey: ['admin-subscriptions', filters],
    queryFn: async () => {
      const { data } = await apiClient.get('/admin/billing/subscriptions', {
        params: filters,
      });
      return data;
    },
  });
}

// Get billing analytics
export function useBillingAnalytics() {
  return useQuery({
    queryKey: ['billing-analytics'],
    queryFn: async () => {
      const { data } = await apiClient.get<BillingAnalytics>(
        '/admin/billing/analytics'
      );
      return data;
    },
  });
}

// Refund transaction
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
        { transaction_id: transactionId, amount_cents: amountCents, reason }
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-subscriptions'] });
      queryClient.invalidateQueries({ queryKey: ['billing-analytics'] });
    },
  });
}

// Grant free subscription
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
      const { data } = await apiClient.post('/admin/billing/grant-free', {
        owner_id: ownerId,
        owner_type: ownerType,
        reason,
        duration_months: durationMonths,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-subscriptions'] });
    },
  });
}

// Admin cancel subscription
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
        { reason, cancel_immediately: cancelImmediately }
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-subscriptions'] });
    },
  });
}

// List all transactions
export function useAdminTransactions(page = 1, pageSize = 50, status?: string) {
  return useQuery({
    queryKey: ['admin-transactions', page, pageSize, status],
    queryFn: async () => {
      const { data } = await apiClient.get('/admin/billing/transactions', {
        params: { page, page_size: pageSize, status },
      });
      return data;
    },
  });
}

// NEW: Billing Manager Management

// List all billing manager relationships
export function useBillingManagerRelationships() {
  return useQuery({
    queryKey: ['billing-manager-relationships'],
    queryFn: async () => {
      const { data } = await apiClient.get<BillingManagerRelationship[]>(
        '/admin/billing/managers'
      );
      return data;
    },
  });
}

// Admin assign billing manager
export function useAdminAssignBillingManager() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ patientId, proxyUserId }: { patientId: string; proxyUserId: string }) => {
      const { data } = await apiClient.put(
        `/admin/patients/${patientId}/billing/manager`,
        { proxy_user_id: proxyUserId }
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-subscriptions'] });
      queryClient.invalidateQueries({ queryKey: ['billing-manager-relationships'] });
    },
  });
}

// Admin remove billing manager
export function useAdminRemoveBillingManager() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (patientId: string) => {
      const { data } = await apiClient.delete(
        `/admin/patients/${patientId}/billing/manager`
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-subscriptions'] });
      queryClient.invalidateQueries({ queryKey: ['billing-manager-relationships'] });
    },
  });
}
```

#### 2. Admin Billing Dashboard: `frontend/src/routes/_auth/admin/billing-management.tsx` (NEW)
```typescript
import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { BillingAnalyticsCards } from '@/components/admin/billing/BillingAnalyticsCards';
import { SubscriptionsList } from '@/components/admin/billing/SubscriptionsList';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TransactionsList } from '@/components/admin/billing/TransactionsList';
import { BillingManagersList } from '@/components/admin/billing/BillingManagersList';

export const Route = createFileRoute('/_auth/admin/billing-management')({
  component: AdminBillingPage,
});

function AdminBillingPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Billing Management</h1>
        <p className="text-muted-foreground">
          Manage subscriptions, process refunds, and view billing analytics
        </p>
      </div>

      {/* Analytics Cards */}
      <BillingAnalyticsCards />

      {/* Tabs for Subscriptions, Transactions, and Billing Managers */}
      <Tabs defaultValue="subscriptions">
        <TabsList>
          <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="billing-managers">Billing Managers</TabsTrigger>
        </TabsList>

        <TabsContent value="subscriptions" className="space-y-4">
          <SubscriptionsList />
        </TabsContent>

        <TabsContent value="transactions" className="space-y-4">
          <TransactionsList />
        </TabsContent>

        <TabsContent value="billing-managers" className="space-y-4">
          <BillingManagersList />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

#### 3. Analytics Cards: `frontend/src/components/admin/billing/BillingAnalyticsCards.tsx` (NEW)
```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useBillingAnalytics } from '@/hooks/api/useAdminBilling';
import { formatCurrency } from '@/lib/utils';
import { TrendingUp, TrendingDown, DollarSign, Users, AlertCircle } from 'lucide-react';

export function BillingAnalyticsCards() {
  const { data: analytics, isLoading } = useBillingAnalytics();

  if (isLoading) {
    return <div>Loading analytics...</div>;
  }

  if (!analytics) return null;

  const cards = [
    {
      title: 'Total MRR',
      value: formatCurrency(analytics.total_mrr_cents / 100),
      icon: DollarSign,
      color: 'text-green-600',
    },
    {
      title: 'Active Subscriptions',
      value: analytics.total_active_subscriptions.toString(),
      icon: Users,
      color: 'text-blue-600',
    },
    {
      title: 'New This Month',
      value: analytics.new_subscriptions_this_month.toString(),
      icon: TrendingUp,
      color: 'text-green-600',
    },
    {
      title: 'Churn Rate',
      value: `${(analytics.churn_rate * 100).toFixed(1)}%`,
      icon: TrendingDown,
      color: 'text-red-600',
    },
    {
      title: 'ARPU',
      value: formatCurrency(analytics.average_revenue_per_user_cents / 100),
      icon: DollarSign,
      color: 'text-purple-600',
    },
    {
      title: 'Failed Payments',
      value: analytics.failed_payments_this_month.toString(),
      icon: AlertCircle,
      color: 'text-orange-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <card.icon className={`h-5 w-5 ${card.color}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

#### 4. Subscriptions List: `frontend/src/components/admin/billing/SubscriptionsList.tsx` (NEW)
```typescript
import { useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useAdminSubscriptions } from '@/hooks/api/useAdminBilling';
import { formatDate, formatCurrency } from '@/lib/utils';
import { MoreHorizontal, Search } from 'lucide-react';
import { SubscriptionActionsMenu } from './SubscriptionActionsMenu';

export function SubscriptionsList() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [ownerTypeFilter, setOwnerTypeFilter] = useState<string | undefined>();

  const { data, isLoading } = useAdminSubscriptions({
    page,
    page_size: 50,
    search,
    status: statusFilter,
    owner_type: ownerTypeFilter,
  });

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'success' | 'warning' | 'destructive' | 'default'> = {
      ACTIVE: 'success',
      TRIALING: 'default',
      PAST_DUE: 'warning',
      CANCELED: 'destructive',
    };
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="ACTIVE">Active</SelectItem>
            <SelectItem value="TRIALING">Trialing</SelectItem>
            <SelectItem value="PAST_DUE">Past Due</SelectItem>
            <SelectItem value="CANCELED">Canceled</SelectItem>
          </SelectContent>
        </Select>
        <Select value={ownerTypeFilter} onValueChange={setOwnerTypeFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="PATIENT">Patients</SelectItem>
            <SelectItem value="ORGANIZATION">Organizations</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      {isLoading ? (
        <div>Loading subscriptions...</div>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Customer</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Billing Manager</TableHead>
                <TableHead>Plan</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>MRR</TableHead>
                <TableHead>Next Billing</TableHead>
                <TableHead>Created</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.subscriptions.map((subscription) => (
                <TableRow key={subscription.owner_id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{subscription.owner_name}</div>
                      <div className="text-sm text-muted-foreground">
                        {subscription.owner_email}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{subscription.owner_type}</Badge>
                  </TableCell>
                  <TableCell>
                    {subscription.billing_manager_name ? (
                      <div className="text-sm">
                        <div className="font-medium">{subscription.billing_manager_name}</div>
                        <div className="text-muted-foreground">Managed</div>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>{subscription.plan_id || 'N/A'}</TableCell>
                  <TableCell>{getStatusBadge(subscription.subscription_status)}</TableCell>
                  <TableCell className="font-semibold">
                    {formatCurrency(subscription.mrr_cents / 100)}
                  </TableCell>
                  <TableCell>
                    {subscription.current_period_end
                      ? formatDate(new Date(subscription.current_period_end))
                      : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {formatDate(new Date(subscription.created_at))}
                  </TableCell>
                  <TableCell>
                    <SubscriptionActionsMenu subscription={subscription} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Showing {data?.subscriptions.length || 0} of {data?.total || 0} subscriptions
              {data && <span className="ml-2 font-semibold">
                Total MRR: {formatCurrency(data.total_mrr_cents / 100)}
              </span>}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(p => p + 1)}
                disabled={!data || data.subscriptions.length < 50}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
```

#### 5. Subscription Actions Menu: `frontend/src/components/admin/billing/SubscriptionActionsMenu.tsx` (NEW)
```typescript
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useGrantFreeSubscription, useAdminCancelSubscription, type SubscriptionListItem } from '@/hooks/api/useAdminBilling';
import { MoreHorizontal, Gift, XCircle, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

interface Props {
  subscription: SubscriptionListItem;
}

export function SubscriptionActionsMenu({ subscription }: Props) {
  const [grantFreeOpen, setGrantFreeOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [reason, setReason] = useState('');
  const [durationMonths, setDurationMonths] = useState<number | undefined>(12);

  const grantFreeMutation = useGrantFreeSubscription();
  const cancelMutation = useAdminCancelSubscription();

  const handleGrantFree = async () => {
    try {
      await grantFreeMutation.mutateAsync({
        ownerId: subscription.owner_id,
        ownerType: subscription.owner_type,
        reason,
        durationMonths,
      });
      toast.success('Free subscription granted successfully');
      setGrantFreeOpen(false);
      setReason('');
    } catch (error) {
      toast.error('Failed to grant free subscription');
    }
  };

  const handleCancel = async (immediately: boolean) => {
    try {
      await cancelMutation.mutateAsync({
        ownerType: subscription.owner_type,
        ownerId: subscription.owner_id,
        reason,
        cancelImmediately: immediately,
      });
      toast.success('Subscription cancelled successfully');
      setCancelOpen(false);
      setReason('');
    } catch (error) {
      toast.error('Failed to cancel subscription');
    }
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem asChild>
            <a
              href={`https://dashboard.stripe.com/customers/${subscription.stripe_customer_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              View in Stripe
            </a>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setGrantFreeOpen(true)}>
            <Gift className="h-4 w-4 mr-2" />
            Grant Free Subscription
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setCancelOpen(true)} className="text-destructive">
            <XCircle className="h-4 w-4 mr-2" />
            Cancel Subscription
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Grant Free Dialog */}
      <Dialog open={grantFreeOpen} onOpenChange={setGrantFreeOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Grant Free Subscription</DialogTitle>
            <DialogDescription>
              Grant a free subscription to {subscription.owner_name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Duration (months)</Label>
              <Input
                type="number"
                value={durationMonths || ''}
                onChange={(e) => setDurationMonths(e.target.value ? Number(e.target.value) : undefined)}
                placeholder="Leave empty for unlimited"
              />
            </div>
            <div>
              <Label>Reason (required)</Label>
              <Textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="e.g., Promotional offer, customer support..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setGrantFreeOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleGrantFree} disabled={!reason || grantFreeMutation.isPending}>
              Grant Free Subscription
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Cancel Dialog */}
      <Dialog open={cancelOpen} onOpenChange={setCancelOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Subscription</DialogTitle>
            <DialogDescription>
              Cancel subscription for {subscription.owner_name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Reason (required)</Label>
              <Textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="e.g., Customer request, payment issues..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelOpen(false)}>
              Keep Subscription
            </Button>
            <Button variant="outline" onClick={() => handleCancel(false)} disabled={!reason || cancelMutation.isPending}>
              Cancel at Period End
            </Button>
            <Button variant="destructive" onClick={() => handleCancel(true)} disabled={!reason || cancelMutation.isPending}>
              Cancel Immediately
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
```

#### 6. Transactions List: `frontend/src/components/admin/billing/TransactionsList.tsx` (NEW)
```typescript
// Similar structure to SubscriptionsList but for transactions
// Includes refund button and modal
// Shows transaction details with receipt links
```

#### 7. Billing Managers List: `frontend/src/components/admin/billing/BillingManagersList.tsx` (NEW)
```typescript
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useBillingManagerRelationships, useAdminRemoveBillingManager } from '@/hooks/api/useAdminBilling';
import { formatDate } from '@/lib/utils';
import { XCircle, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useState } from 'react';

export function BillingManagersList() {
  const { data: relationships, isLoading } = useBillingManagerRelationships();
  const removeMutation = useAdminRemoveBillingManager();
  const [confirmRemove, setConfirmRemove] = useState<string | null>(null);

  const handleRemove = async (patientId: string) => {
    try {
      await removeMutation.mutateAsync(patientId);
      toast.success('Billing manager removed successfully');
      setConfirmRemove(null);
    } catch (error) {
      toast.error('Failed to remove billing manager');
    }
  };

  if (isLoading) {
    return <div>Loading billing managers...</div>;
  }

  if (!relationships || relationships.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No billing manager relationships found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {relationships.length} billing manager relationship{relationships.length !== 1 ? 's' : ''}
        </p>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Patient</TableHead>
            <TableHead>Billing Manager</TableHead>
            <TableHead>Assigned At</TableHead>
            <TableHead>Assigned By</TableHead>
            <TableHead></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {relationships.map((relationship) => (
            <TableRow key={relationship.patient_id}>
              <TableCell>
                <div>
                  <div className="font-medium">{relationship.patient_name}</div>
                  <div className="text-sm text-muted-foreground">
                    {relationship.patient_email}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <div>
                  <div className="font-medium">{relationship.billing_manager_name}</div>
                  <div className="text-sm text-muted-foreground">
                    {relationship.billing_manager_email}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                {formatDate(new Date(relationship.assigned_at))}
              </TableCell>
              <TableCell>
                <Badge variant="outline">{relationship.assigned_by_name}</Badge>
              </TableCell>
              <TableCell>
                <Dialog open={confirmRemove === relationship.patient_id} onOpenChange={(open) => !open && setConfirmRemove(null)}>
                  <DialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setConfirmRemove(relationship.patient_id)}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Remove
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Remove Billing Manager</DialogTitle>
                      <DialogDescription>
                        Remove {relationship.billing_manager_name} as billing manager for {relationship.patient_name}?
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setConfirmRemove(null)}>
                        Cancel
                      </Button>
                      <Button
                        variant="destructive"
                        onClick={() => handleRemove(relationship.patient_id)}
                        disabled={removeMutation.isPending}
                      >
                        Remove Billing Manager
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
```

## Acceptance Criteria
### Billing Dashboard
- [ ] Admin billing dashboard displays analytics cards.
- [ ] Dashboard has three tabs: Subscriptions, Transactions, and Billing Managers.

### Subscriptions Management
- [ ] Subscriptions list loads with pagination.
- [ ] Search by name/email works correctly.
- [ ] Status and type filters work.
- [ ] Subscriptions table shows billing manager column.
- [ ] Billing manager column displays manager name or "—" if none.
- [ ] Actions menu allows granting free subscription.
- [ ] Actions menu allows cancelling subscription.
- [ ] Stripe dashboard link opens correctly.

### Transactions Management
- [ ] Transactions tab shows all transactions.
- [ ] Refund dialog works for transactions.

### Billing Managers Management
- [ ] Billing Managers tab shows all relationships.
- [ ] List displays patient name, manager name, assigned date, and assigner.
- [ ] Remove billing manager button works correctly.
- [ ] Confirmation dialog shown before removing.
- [ ] Real-time updates after removal.

### General
- [ ] Real-time updates after actions.
- [ ] Loading and error states handled.
- [ ] Responsive on all screen sizes.

## Verification Plan
**Automated Tests:**
```bash
pnpm test src/components/admin/billing --run
pnpm exec playwright test e2e/admin-billing.spec.ts
```

**Manual Verification:**
1. Login as admin
2. View billing dashboard
3. Filter subscriptions by status
4. Search for a customer
5. Verify billing manager column shows correctly in subscriptions table
6. Grant free subscription
7. Cancel a subscription
8. View transaction details
9. Issue a refund
10. Navigate to Billing Managers tab
11. View all billing manager relationships
12. Remove a billing manager
13. Verify analytics update

## Rollback Plan
If issues arise:
1. Disable admin billing page via feature flag
2. Use Stripe dashboard temporarily
3. Fix issues in staging
4. Re-enable after verification
