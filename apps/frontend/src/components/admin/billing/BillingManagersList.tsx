import { XCircle } from "lucide-react";
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
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useAdminRemoveBillingManager,
  useBillingManagerRelationships,
} from "@/hooks/api/useAdminBilling";
import { formatDate } from "@/lib/utils";

export function BillingManagersList() {
  const { data: relationships, isLoading } = useBillingManagerRelationships();
  const removeMutation = useAdminRemoveBillingManager();
  const [confirmRemove, setConfirmRemove] = useState<string | null>(null);

  const handleRemove = async () => {
    if (!confirmRemove) return;
    try {
      await removeMutation.mutateAsync(confirmRemove);
      toast.success("Billing manager removed successfully");
      setConfirmRemove(null);
    } catch {
      toast.error("Failed to remove billing manager");
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (!relationships || relationships.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">
          No billing manager relationships found
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Billing managers are proxies who manage billing on behalf of patients.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {relationships.length} billing manager relationship
          {relationships.length !== 1 ? "s" : ""}
        </p>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Patient</TableHead>
              <TableHead>Billing Manager</TableHead>
              <TableHead>Assigned At</TableHead>
              <TableHead>Assigned By</TableHead>
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {relationships.map((relationship) => (
              <TableRow key={relationship.patient_id}>
                <TableCell>
                  <div>
                    <div className="font-medium">
                      {relationship.patient_name}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {relationship.patient_email}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <div>
                    <div className="font-medium">
                      {relationship.billing_manager_name}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {relationship.billing_manager_email}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  {formatDate(new Date(relationship.assigned_at))}
                </TableCell>
                <TableCell>
                  <div className="text-sm">{relationship.assigned_by_name}</div>
                </TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive hover:text-destructive"
                    onClick={() => setConfirmRemove(relationship.patient_id)}
                  >
                    <XCircle className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Remove Confirmation Dialog */}
      <Dialog
        open={!!confirmRemove}
        onOpenChange={() => setConfirmRemove(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Remove Billing Manager</DialogTitle>
            <DialogDescription>
              Are you sure you want to remove this billing manager? The patient
              will need to manage their own billing or have a new manager
              assigned.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmRemove(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleRemove}
              disabled={removeMutation.isPending}
            >
              {removeMutation.isPending
                ? "Removing..."
                : "Remove Billing Manager"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
