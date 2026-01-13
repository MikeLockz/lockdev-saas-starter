import { createFileRoute } from '@tanstack/react-router'
import { useManagedPatientSubscription } from '@/hooks/api/useProxyBilling';

export const Route = createFileRoute('/_auth/proxy/managed-patients/$managedPatientId/billing')({
    component: ManagedPatientBillingDetail,
});

function ManagedPatientBillingDetail() {
    const { managedPatientId } = Route.useParams();

    // We use the proxy-specific hook to fetch subscription details
    // Note: The backend endpoint for proxy getting patient subscription returns similar structure to patient's own view
    const { data: subscription, isLoading } = useManagedPatientSubscription(managedPatientId);

    if (isLoading) {
        return <div>Loading billing information...</div>;
    }

    const hasActiveSubscription = subscription?.status === 'ACTIVE' || subscription?.status === 'TRIALING';

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <h1 className="text-3xl font-bold mb-6">Manage Billing</h1>

            {/* We can probably reuse the PatientSubscriptionCard since the structure is likely same or very similar */}
            {/* However, the mutations inside PatientSubscriptionCard use usePatientBillingPortal which hits /patients/:id endpoints */}
            {/* Proxies need to hit /proxy/managed-patients/:id endpoints */}
            {/* For now, let's assume we need to make PatientSubscriptionCard aware of context OR make a ProxySubscriptionCard */}
            {/* Actually, looking at PatientSubscriptionCard, it imports hooks directly. We should refactor it to accept callbacks or build a wrapper. */}
            {/* For expediency, I will duplicate the card logic for Proxy context or create a wrapper if time permits. */}
            {/* Let's use a specialized ProxySubscriptionManager component here to keep it clean. */}

            <ProxySubscriptionManager
                subscription={subscription}
                patientId={managedPatientId}
                hasActiveSubscription={hasActiveSubscription}
            />

            {!hasActiveSubscription && (
                <div className="mb-8">
                    <h2 className="text-2xl font-semibold mb-4">Choose a Plan</h2>
                    {/* PatientPlanSelector uses usePatientCheckout - we need ProxyPlanSelector or prop for mutation */}
                    <ProxyPlanSelector patientId={managedPatientId} />
                </div>
            )}

            {hasActiveSubscription && (
                <div>
                    <h2 className="text-2xl font-semibold mb-4">Payment History</h2>
                    {/* TransactionHistory uses usePatientTransactions - we need ProxyTransactionHistory */}
                    <ProxyTransactionHistory patientId={managedPatientId} />
                </div>
            )}

        </div>
    );
}

// --- Inline Components for Proxy Context (to be extracted if grown) ---

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { useProxyCancelSubscription, useProxyCheckout, useManagedPatientTransactions } from '@/hooks/api/useProxyBilling';
import { formatDate, formatCurrency } from '@/lib/utils';
import { CreditCard, AlertCircle, Download } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

function ProxySubscriptionManager({ subscription, patientId }: any) {
    const cancelMutation = useProxyCancelSubscription(patientId);
    // Proxies might not have portal access for patients easily, or it might be different. 
    // API spec didn't mention portal for proxy, but checkout/cancel yes.

    const getStatusBadge = (status: string) => {
        const variants: Record<string, "default" | "destructive" | "outline" | "secondary"> = {
            ACTIVE: 'default',
            TRIALING: 'secondary',
            PAST_DUE: 'outline',
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
                        This patient doesn't have an active subscription. Choose a plan below to get them started.
                    </CardDescription>
                </CardHeader>
            </Card>
        );
    }

    return (
        <Card className="mb-8">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <CreditCard className="h-5 w-5" />
                            Current Subscription
                        </CardTitle>
                        <CardDescription className="mt-2">
                            Manage subscription
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
                            Subscription cancelled at period end.
                        </p>
                    </div>
                )}

                <div className="flex gap-3">
                    {!subscription.cancel_at_period_end && (
                        <AlertDialog>
                            <AlertDialogTrigger asChild>
                                <Button variant="outline">Cancel Subscription</Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                                <AlertDialogHeader>
                                    <AlertDialogTitle>Cancel Subscription?</AlertDialogTitle>
                                    <AlertDialogDescription>
                                        You can cancel the subscription immediately or at the end of the current billing period.
                                    </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                    <AlertDialogCancel>Keep Subscription</AlertDialogCancel>
                                    <AlertDialogAction
                                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                        onClick={() => cancelMutation.mutate({ cancelImmediately: false })}
                                    >
                                        Cancel at Period End
                                    </AlertDialogAction>
                                    <AlertDialogAction
                                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
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
    )
}

function ProxyPlanSelector({ patientId }: { patientId: string }) {
    const checkoutMutation = useProxyCheckout(patientId);

    // Duplicating PLANS constant for now, should be shared
    const PLANS = [
        {
            id: 'price_starter',
            name: 'Starter',
            price: 29,
            features: ['Basic', 'Email reminders'], // Simplified for brevity or import from shared
        },
        {
            id: 'price_professional',
            name: 'Professional',
            price: 79,
            popular: true,
            features: ['Everything in Starter', 'Advanced'],
        },
        {
            id: 'price_enterprise',
            name: 'Enterprise',
            price: 199,
            features: ['Everything in Professional', 'Unlimited'],
        },
    ];

    return (
        <div className="grid md:grid-cols-3 gap-6">
            {PLANS.map((plan) => (
                <Card key={plan.id} className={plan.popular ? 'border-primary shadow-lg' : ''}>
                    <CardHeader>
                        <CardTitle>{plan.name}</CardTitle>
                        <CardDescription><span className="text-3xl font-bold">${plan.price}</span>/mo</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Button
                            className="w-full"
                            onClick={() => checkoutMutation.mutate(plan.id)}
                            disabled={checkoutMutation.isPending}
                        >
                            {checkoutMutation.isPending ? 'Loading...' : 'Select Plan'}
                        </Button>
                    </CardContent>
                </Card>
            ))}
        </div>
    )
}

function ProxyTransactionHistory({ patientId }: { patientId: string }) {
    const { data, isLoading } = useManagedPatientTransactions(patientId);
    const getStatusBadge = (status: string) => {
        const variants: Record<string, "default" | "destructive" | "outline" | "secondary"> = {
            SUCCEEDED: 'default', PENDING: 'secondary', FAILED: 'destructive', REFUNDED: 'outline',
        };
        return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
    };

    if (isLoading) return <div>Loading transactions...</div>

    return (
        <Card>
            <CardHeader><CardTitle>Transaction History</CardTitle></CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Date</TableHead>
                            <TableHead>Amount</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Receipt</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data?.transactions.map((tx: any) => (
                            <TableRow key={tx.id}>
                                <TableCell>{formatDate(new Date(tx.created_at))}</TableCell>
                                <TableCell>{formatCurrency(tx.amount_cents / 100)}</TableCell>
                                <TableCell>{getStatusBadge(tx.status)}</TableCell>
                                <TableCell>
                                    {tx.receipt_url && (
                                        <Button variant="ghost" size="sm" asChild>
                                            <a href={tx.receipt_url} target="_blank" rel="noopener noreferrer">
                                                <Download className="h-4 w-4 mr-2" /> Receipt
                                            </a>
                                        </Button>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                        {!data?.transactions.length && (
                            <TableRow><TableCell colSpan={4} className="text-center">No transactions</TableCell></TableRow>
                        )}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    )
}
