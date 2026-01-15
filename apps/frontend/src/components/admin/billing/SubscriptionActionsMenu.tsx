import { ExternalLink, Gift, MoreHorizontal, XCircle } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  type SubscriptionListItem,
  useAdminCancelSubscription,
  useGrantFreeSubscription,
} from "@/hooks/api/useAdminBilling";

interface Props {
  subscription: SubscriptionListItem;
}

export function SubscriptionActionsMenu({ subscription }: Props) {
  const [grantFreeOpen, setGrantFreeOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [reason, setReason] = useState("");
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
      toast.success("Free subscription granted successfully");
      setGrantFreeOpen(false);
      setReason("");
    } catch {
      toast.error("Failed to grant free subscription");
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
      toast.success("Subscription cancelled successfully");
      setCancelOpen(false);
      setReason("");
    } catch {
      toast.error("Failed to cancel subscription");
    }
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <span className="sr-only">Open menu</span>
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {subscription.stripe_customer_id && (
            <>
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
              <DropdownMenuSeparator />
            </>
          )}
          <DropdownMenuItem onClick={() => setGrantFreeOpen(true)}>
            <Gift className="h-4 w-4 mr-2" />
            Grant Free Subscription
          </DropdownMenuItem>
          {subscription.subscription_status === "ACTIVE" && (
            <DropdownMenuItem
              onClick={() => setCancelOpen(true)}
              className="text-destructive focus:text-destructive"
            >
              <XCircle className="h-4 w-4 mr-2" />
              Cancel Subscription
            </DropdownMenuItem>
          )}
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
            <div className="space-y-2">
              <Label htmlFor="duration">Duration (months)</Label>
              <Input
                id="duration"
                type="number"
                value={durationMonths || ""}
                onChange={(e) =>
                  setDurationMonths(
                    e.target.value ? Number(e.target.value) : undefined,
                  )
                }
                placeholder="Leave empty for unlimited"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="reason">Reason (required)</Label>
              <Textarea
                id="reason"
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
            <Button
              onClick={handleGrantFree}
              disabled={!reason || grantFreeMutation.isPending}
            >
              {grantFreeMutation.isPending
                ? "Granting..."
                : "Grant Free Subscription"}
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
            <div className="space-y-2">
              <Label htmlFor="cancel-reason">Reason (required)</Label>
              <Textarea
                id="cancel-reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="e.g., Customer request, payment issues..."
              />
            </div>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="outline" onClick={() => setCancelOpen(false)}>
              Keep Subscription
            </Button>
            <Button
              variant="outline"
              onClick={() => handleCancel(false)}
              disabled={!reason || cancelMutation.isPending}
            >
              Cancel at Period End
            </Button>
            <Button
              variant="destructive"
              onClick={() => handleCancel(true)}
              disabled={!reason || cancelMutation.isPending}
            >
              Cancel Immediately
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
