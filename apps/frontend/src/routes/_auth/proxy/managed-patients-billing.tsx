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
        const variants: Record<string, "default" | "destructive" | "outline" | "secondary"> = {
            ACTIVE: 'default',
            TRIALING: 'secondary',
            PAST_DUE: 'outline',
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
                    {subscriptions?.map((sub: any) => (
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
                                                {formatDate(new Date(sub.current_period_end * 1000))}
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
