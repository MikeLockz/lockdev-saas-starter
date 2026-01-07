import { CreditCard, ExternalLink, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useBillingPortal, useSubscription } from "@/hooks/api/useBilling";

const statusColors: Record<string, string> = {
  ACTIVE: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  TRIALING: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  PAST_DUE:
    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  CANCELED: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  CANCELLED: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  NONE: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

function formatDate(timestamp: number | null): string {
  if (!timestamp) return "N/A";
  return new Date(timestamp * 1000).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function SubscriptionCard() {
  const { data: subscription, isLoading, error } = useSubscription();
  const billingPortal = useBillingPortal();

  const handleManageBilling = () => {
    billingPortal.mutate();
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-10 w-40" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-destructive">
            Error Loading Subscription
          </CardTitle>
          <CardDescription>{error.message}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const hasSubscription = subscription && subscription.status !== "NONE";
  const statusClass =
    statusColors[subscription?.status || "NONE"] || statusColors.NONE;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CreditCard className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Subscription</CardTitle>
          </div>
          {hasSubscription && (
            <Badge className={statusClass}>{subscription.status}</Badge>
          )}
        </div>
        <CardDescription>
          {hasSubscription
            ? "Manage your organization's subscription and billing"
            : "Subscribe to unlock premium features"}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {hasSubscription ? (
          <>
            {subscription.plan_id && (
              <div className="text-sm">
                <span className="text-muted-foreground">Plan: </span>
                <span className="font-medium">{subscription.plan_id}</span>
              </div>
            )}
            {subscription.current_period_end && (
              <div className="text-sm">
                <span className="text-muted-foreground">
                  Next billing date:{" "}
                </span>
                <span className="font-medium">
                  {formatDate(subscription.current_period_end)}
                </span>
              </div>
            )}
            {subscription.cancel_at_period_end && (
              <div className="text-sm text-yellow-600 dark:text-yellow-400">
                Subscription will cancel at end of billing period
              </div>
            )}
            <Button
              onClick={handleManageBilling}
              disabled={billingPortal.isPending}
              className="mt-4"
            >
              {billingPortal.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Manage Subscription
                </>
              )}
            </Button>
          </>
        ) : (
          <div className="text-center py-4">
            <p className="text-muted-foreground mb-4">
              No active subscription. Choose a plan to get started.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
