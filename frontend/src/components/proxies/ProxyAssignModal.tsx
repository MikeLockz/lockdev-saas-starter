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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { PermissionGroup, PERMISSION_CATEGORIES } from "./PermissionToggle";
import { useAssignProxy, type ProxyPermissions } from "@/hooks/api/usePatientProxies";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

const RELATIONSHIP_TYPES = [
    { value: "PARENT", label: "Parent" },
    { value: "SPOUSE", label: "Spouse" },
    { value: "GUARDIAN", label: "Legal Guardian" },
    { value: "CAREGIVER", label: "Caregiver" },
    { value: "POA", label: "Power of Attorney" },
    { value: "OTHER", label: "Other" },
] as const;

const DEFAULT_PERMISSIONS: ProxyPermissions = {
    can_view_profile: true,
    can_view_appointments: true,
    can_schedule_appointments: false,
    can_view_clinical_notes: false,
    can_view_billing: false,
    can_message_providers: false,
};

interface ProxyAssignModalProps {
    patientId: string;
    patientName?: string;
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function ProxyAssignModal({
    patientId,
    patientName,
    open,
    onOpenChange,
}: ProxyAssignModalProps) {
    const [email, setEmail] = useState("");
    const [relationshipType, setRelationshipType] = useState<string>("");
    const [permissions, setPermissions] = useState<ProxyPermissions>(DEFAULT_PERMISSIONS);
    const assignProxy = useAssignProxy(patientId);

    const handlePermissionChange = (key: string, value: boolean) => {
        setPermissions((prev) => ({ ...prev, [key]: value }));
    };

    const handleSubmit = async () => {
        if (!email || !relationshipType) {
            toast.error("Missing Information", {
                description: "Please enter an email and select a relationship type.",
            });
            return;
        }

        try {
            await assignProxy.mutateAsync({
                email,
                relationship_type: relationshipType,
                permissions,
            });
            toast.success("Proxy Assigned", {
                description: `Successfully granted proxy access to ${email}.`,
            });
            handleClose();
        } catch (error: unknown) {
            const message = error instanceof Error ? error.message : "Failed to assign proxy";
            toast.error("Error", {
                description: message,
            });
        }
    };

    const handleClose = () => {
        setEmail("");
        setRelationshipType("");
        setPermissions(DEFAULT_PERMISSIONS);
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Add Proxy Access</DialogTitle>
                    <DialogDescription>
                        Grant someone access to manage{" "}
                        {patientName ? `${patientName}'s` : "this patient's"} health records.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 py-4">
                    {/* Email Input */}
                    <div className="space-y-2">
                        <Label htmlFor="proxy-email">Email Address</Label>
                        <Input
                            id="proxy-email"
                            type="email"
                            placeholder="proxy@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        <p className="text-xs text-muted-foreground">
                            The user must have an existing account.
                        </p>
                    </div>

                    {/* Relationship Type */}
                    <div className="space-y-2">
                        <Label>Relationship</Label>
                        <Select value={relationshipType} onValueChange={setRelationshipType}>
                            <SelectTrigger>
                                <SelectValue placeholder="Select relationship..." />
                            </SelectTrigger>
                            <SelectContent>
                                {RELATIONSHIP_TYPES.map((type) => (
                                    <SelectItem key={type.value} value={type.value}>
                                        {type.label}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Permissions */}
                    <div className="space-y-4">
                        <Label>Permissions</Label>
                        {(Object.keys(PERMISSION_CATEGORIES) as Array<keyof typeof PERMISSION_CATEGORIES>).map((category) => (
                            <PermissionGroup
                                key={category}
                                category={category}
                                permissions={permissions as unknown as { [key: string]: boolean }}
                                onPermissionChange={handlePermissionChange}
                            />
                        ))}
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={handleClose}>
                        Cancel
                    </Button>
                    <Button onClick={handleSubmit} disabled={assignProxy.isPending}>
                        {assignProxy.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Grant Access
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
