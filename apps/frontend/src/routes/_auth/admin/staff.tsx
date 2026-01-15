import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { RoleGuard } from "@/components/auth/RoleGuard";
import { StaffForm } from "@/components/staff/StaffForm";
import { StaffTable } from "@/components/staff/StaffTable";
import type { StaffListItem } from "@/hooks/useStaff";

export const Route = createFileRoute("/_auth/admin/staff")({
  component: StaffPage,
});

function StaffPage() {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState<StaffListItem | null>(
    null,
  );

  const handleCreate = () => {
    setSelectedStaff(null);
    setIsFormOpen(true);
  };

  const handleEdit = (staff: StaffListItem) => {
    setSelectedStaff(staff);
    setIsFormOpen(true);
  };

  return (
    <RoleGuard allowedRoles={["admin", "super_admin"]}>
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium">Staff</h3>
          <p className="text-sm text-muted-foreground">
            Manage administrative and support staff.
          </p>
        </div>

        <StaffTable onCreate={handleCreate} onEdit={handleEdit} />

        <StaffForm
          open={isFormOpen}
          onOpenChange={setIsFormOpen}
          staff={selectedStaff}
        />
      </div>
    </RoleGuard>
  );
}
