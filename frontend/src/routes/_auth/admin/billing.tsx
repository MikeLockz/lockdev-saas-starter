import { createFileRoute } from "@tanstack/react-router";
import { SubscriptionCard, PlanSelector } from "@/components/billing";
import { useSubscription } from "@/hooks/api/useBilling";

export const Route = createFileRoute("/_auth/admin/billing")({
    component: BillingPage,
});

function BillingPage() {
    const { data: subscription } = useSubscription();
    const hasSubscription = subscription && subscription.status !== "NONE";

    return (
        <div className="container mx-auto py-8 space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
                <p className="text-muted-foreground">
                    Manage your organization's subscription and billing settings
                </p>
            </div>

            {/* Current Subscription */}
            <section>
                <SubscriptionCard />
            </section>

            {/* Plans Section */}
            {!hasSubscription && (
                <section className="space-y-4">
                    <div>
                        <h2 className="text-2xl font-semibold">Choose a Plan</h2>
                        <p className="text-muted-foreground">
                            Select the plan that best fits your organization's needs
                        </p>
                    </div>
                    <PlanSelector currentPlanId={subscription?.plan_id} />
                </section>
            )}

            {/* Upgrade Section (show plans if already subscribed) */}
            {hasSubscription && (
                <section className="space-y-4">
                    <div>
                        <h2 className="text-2xl font-semibold">Upgrade Your Plan</h2>
                        <p className="text-muted-foreground">
                            Looking for more features? Compare our plans below.
                        </p>
                    </div>
                    <PlanSelector currentPlanId={subscription?.plan_id} />
                </section>
            )}
        </div>
    );
}
