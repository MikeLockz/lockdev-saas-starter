import { MoreHorizontal, Shield, Trash2, UserPlus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
  type ProxyAssignment,
  usePatientProxies,
  useRevokeProxy,
} from "@/hooks/api/usePatientProxies";
import { ProxyAssignModal } from "./ProxyAssignModal";
import { ProxyEditModal } from "./ProxyEditModal";

const RELATIONSHIP_LABELS: Record<string, string> = {
  PARENT: "Parent",
  SPOUSE: "Spouse",
  GUARDIAN: "Guardian",
  CAREGIVER: "Caregiver",
  POA: "Power of Attorney",
  OTHER: "Other",
};

interface ProxyListProps {
  patientId: string;
  patientName?: string;
}

export function ProxyList({ patientId, patientName }: ProxyListProps) {
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [editProxy, setEditProxy] = useState<ProxyAssignment | null>(null);
  const [revokeProxy, setRevokeProxy] = useState<ProxyAssignment | null>(null);
  const { data, isLoading, error } = usePatientProxies(patientId);
  const revokeProxyMutation = useRevokeProxy(patientId);

  const handleRevoke = async () => {
    if (!revokeProxy) return;
    try {
      await revokeProxyMutation.mutateAsync(revokeProxy.id);
      toast.success("Access Revoked", {
        description: `Proxy access for ${revokeProxy.user.display_name || revokeProxy.user.email} has been revoked.`,
      });
      setRevokeProxy(null);
    } catch {
      toast.error("Error", {
        description: "Failed to revoke proxy access.",
      });
    }
  };

  const getPermissionCount = (proxy: ProxyAssignment) => {
    const perms = [
      proxy.can_view_profile,
      proxy.can_view_appointments,
      proxy.can_schedule_appointments,
      proxy.can_view_clinical_notes,
      proxy.can_view_billing,
      proxy.can_message_providers,
    ];
    return perms.filter(Boolean).length;
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="border rounded-lg p-4 space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-destructive">
        Error loading proxies. Please try again.
      </div>
    );
  }

  const proxies = data?.proxies ?? [];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">Authorized Proxies</h3>
          <p className="text-sm text-muted-foreground">
            People who can access and manage this patient's records
          </p>
        </div>
        <Button onClick={() => setAssignModalOpen(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          Add Proxy
        </Button>
      </div>

      {proxies.length === 0 ? (
        <div className="border rounded-lg p-8 text-center">
          <Shield className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <h4 className="font-medium mb-2">No Proxies Assigned</h4>
          <p className="text-sm text-muted-foreground mb-4">
            Grant access to family members or caregivers to help manage care.
          </p>
          <Button onClick={() => setAssignModalOpen(true)}>
            <UserPlus className="mr-2 h-4 w-4" />
            Add First Proxy
          </Button>
        </div>
      ) : (
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Relationship</TableHead>
                <TableHead>Permissions</TableHead>
                <TableHead>Granted</TableHead>
                <TableHead className="w-[70px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {proxies.map((proxy) => (
                <TableRow key={proxy.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">
                        {proxy.user.display_name || "—"}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {proxy.user.email}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {RELATIONSHIP_LABELS[proxy.relationship_type] ||
                        proxy.relationship_type}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm">
                      {getPermissionCount(proxy)} of 6 enabled
                    </span>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-muted-foreground">
                      {new Date(proxy.granted_at).toLocaleDateString()}
                    </span>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => setEditProxy(proxy)}>
                          <Shield className="mr-2 h-4 w-4" />
                          Edit Permissions
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => setRevokeProxy(proxy)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Revoke Access
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      <ProxyAssignModal
        patientId={patientId}
        patientName={patientName}
        open={assignModalOpen}
        onOpenChange={setAssignModalOpen}
      />

      {editProxy && (
        <ProxyEditModal
          patientId={patientId}
          proxy={editProxy}
          open={!!editProxy}
          onOpenChange={(open: boolean) => !open && setEditProxy(null)}
        />
      )}

      <AlertDialog
        open={!!revokeProxy}
        onOpenChange={(open) => !open && setRevokeProxy(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Revoke Proxy Access?</AlertDialogTitle>
            <AlertDialogDescription>
              This will immediately revoke access for{" "}
              <strong>
                {revokeProxy?.user.display_name || revokeProxy?.user.email}
              </strong>
              . They will no longer be able to view or manage this patient's
              records.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleRevoke}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Revoke Access
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
