import { AlertCircle, CreditCard } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  type PatientSubscription,
  useCancelPatientSubscription,
  usePatientBillingPortal,
} from "@/hooks/api/usePatientBilling";
import { formatDate } from "@/lib/utils";

interface Props {
  subscription: PatientSubscription | undefined;
  patientId: string;
}

export function PatientSubscriptionCard({ subscription, patientId }: Props) {
  const portalMutation = usePatientBillingPortal(patientId);
  const cancelMutation = useCancelPatientSubscription(patientId);

  const getStatusBadge = (status: string) => {
    const variants: Record<
      string,
      "default" | "destructive" | "outline" | "secondary"
    > = {
      ACTIVE: "default", // success -> default (or use className for green)
      TRIALING: "secondary",
      PAST_DUE: "outline", // warning -> outline
      CANCELED: "destructive",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  if (!subscription || subscription.status === "NONE") {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Active Subscription</CardTitle>
          <CardDescription>
            You don't have an active subscription yet. Choose a plan below to
            get started.
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
            <p className="text-lg font-semibold">
              {subscription.plan_id || "Unknown"}
            </p>
          </div>
          {subscription.current_period_end && (
            <div>
              <p className="text-sm text-muted-foreground">
                {subscription.cancel_at_period_end
                  ? "Cancels on"
                  : "Next billing date"}
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
              Your subscription will be cancelled at the end of the current
              billing period.
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
                    You can cancel your subscription immediately or at the end
                    of your current billing period. If you cancel now, you'll
                    lose access immediately. If you cancel at period end, you'll
                    retain access until{" "}
                    {formatDate(
                      new Date(subscription.current_period_end! * 1000),
                    )}
                    .
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Keep Subscription</AlertDialogCancel>
                  <AlertDialogAction
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    onClick={() =>
                      cancelMutation.mutate({ cancelImmediately: false })
                    }
                  >
                    Cancel at Period End
                  </AlertDialogAction>
                  <AlertDialogAction
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    onClick={() =>
                      cancelMutation.mutate({ cancelImmediately: true })
                    }
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
