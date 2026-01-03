import { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { PermissionGroup, PERMISSION_CATEGORIES } from "./PermissionToggle";
import { useUpdateProxyPermissions, type ProxyAssignment, type ProxyPermissions } from "@/hooks/api/usePatientProxies";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

interface ProxyEditModalProps {
    patientId: string;
    proxy: ProxyAssignment;
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function ProxyEditModal({
    patientId,
    proxy,
    open,
    onOpenChange,
}: ProxyEditModalProps) {
    const [permissions, setPermissions] = useState<ProxyPermissions>({
        can_view_profile: proxy.can_view_profile,
        can_view_appointments: proxy.can_view_appointments,
        can_schedule_appointments: proxy.can_schedule_appointments,
        can_view_clinical_notes: proxy.can_view_clinical_notes,
        can_view_billing: proxy.can_view_billing,
        can_message_providers: proxy.can_message_providers,
    });
    const updatePermissions = useUpdateProxyPermissions(patientId);

    const handlePermissionChange = (key: string, value: boolean) => {
        setPermissions((prev) => ({ ...prev, [key]: value }));
    };

    const handleSubmit = async () => {
        try {
            await updatePermissions.mutateAsync({
                assignmentId: proxy.id,
                data: { permissions },
            });
            toast.success("Permissions Updated", {
                description: `Permissions for ${proxy.user.display_name || proxy.user.email} have been updated.`,
            });
            onOpenChange(false);
        } catch {
            toast.error("Error", {
                description: "Failed to update permissions.",
            });
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Edit Proxy Permissions</DialogTitle>
                    <DialogDescription>
                        Update permissions for{" "}
                        <strong>{proxy.user.display_name || proxy.user.email}</strong>
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    {(Object.keys(PERMISSION_CATEGORIES) as Array<keyof typeof PERMISSION_CATEGORIES>).map((category) => (
                        <PermissionGroup
                            key={category}
                            category={category}
                            permissions={permissions as unknown as { [key: string]: boolean }}
                            onPermissionChange={handlePermissionChange}
                        />
                    ))}
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)}>
                        Cancel
                    </Button>
                    <Button onClick={handleSubmit} disabled={updatePermissions.isPending}>
                        {updatePermissions.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Save Changes
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
