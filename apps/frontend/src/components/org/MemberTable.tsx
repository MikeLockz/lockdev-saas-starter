import { MoreHorizontal, Shield, ShieldOff } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
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
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useTimezoneContext } from "@/contexts/TimezoneContext";
import { useCurrentOrg } from "@/hooks/useCurrentOrg";
import { useOrgMembers } from "@/hooks/useOrgMembers";
import { formatDateTime } from "@/lib/timezone";

const ROLE_OPTIONS = [
  { value: "admin", label: "Admin" },
  { value: "staff", label: "Staff" },
  { value: "provider", label: "Provider" },
  { value: "patient", label: "Patient" },
];

interface Member {
  id: string;
  email: string;
  display_name?: string;
  role: string;
  created_at?: string;
  mfa_enabled?: boolean;
}

export function MemberTable() {
  const timezone = useTimezoneContext();
  const { orgId } = useCurrentOrg();
  const { data: members, isLoading } = useOrgMembers(orgId);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<Member | null>(null);
  const [newRole, setNewRole] = useState<string>("");
  const [isUpdating, setIsUpdating] = useState(false);

  const handleOpenRoleModal = (member: Member) => {
    setSelectedMember(member);
    setNewRole(member.role);
    setRoleModalOpen(true);
  };

  const handleRoleChange = async () => {
    if (!selectedMember || !newRole) return;

    setIsUpdating(true);
    try {
      // TODO: Implement actual API call to update member role
      // await updateMemberRole(selectedMember.id, newRole);
      await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate API call
      toast.success(
        `Role updated to ${newRole} for ${selectedMember.display_name || selectedMember.email}`,
      );
      setRoleModalOpen(false);
    } catch (error) {
      toast.error("Failed to update role");
      console.error("Role update error:", error);
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    );
  }

  if (!members || members.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-muted-foreground border rounded-md">
        No members found in this organization.
      </div>
    );
  }

  return (
    <>
      <div className="rounded-md border">
        <table className="w-full caption-bottom text-sm">
          <thead className="[&_tr]:border-b">
            <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Name
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Email
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Role
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                MFA Status
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Joined At
              </th>
              <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="[&_tr:last-child]:border-0">
            {members.map((member) => (
              <tr
                key={member.id}
                className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
              >
                <td className="p-4 align-middle font-medium">
                  {member.display_name || "Unknown"}
                </td>
                <td className="p-4 align-middle">{member.email}</td>
                <td className="p-4 align-middle capitalize">{member.role}</td>
                <td className="p-4 align-middle">
                  {member.mfa_enabled ? (
                    <Badge
                      variant="default"
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Shield className="h-3 w-3 mr-1" />
                      MFA Enabled
                    </Badge>
                  ) : (
                    <Badge variant="outline">
                      <ShieldOff className="h-3 w-3 mr-1" />
                      MFA Off
                    </Badge>
                  )}
                </td>
                <td className="p-4 align-middle">
                  {member.created_at
                    ? formatDateTime(
                        new Date(member.created_at),
                        "MMM d, yyyy",
                        timezone,
                      )
                    : "-"}
                </td>
                <td className="p-4 align-middle text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                        <span className="sr-only">Actions</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() => handleOpenRoleModal(member)}
                      >
                        Change Role
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Role Change Modal */}
      <Dialog open={roleModalOpen} onOpenChange={setRoleModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change Member Role</DialogTitle>
            <DialogDescription>
              Change the role for{" "}
              {selectedMember?.display_name || selectedMember?.email}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select value={newRole} onValueChange={setNewRole}>
              <SelectTrigger>
                <SelectValue placeholder="Select role" />
              </SelectTrigger>
              <SelectContent>
                {ROLE_OPTIONS.map((role) => (
                  <SelectItem key={role.value} value={role.value}>
                    {role.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRoleModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleRoleChange}
              disabled={isUpdating || newRole === selectedMember?.role}
            >
              {isUpdating ? "Updating..." : "Update Role"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
