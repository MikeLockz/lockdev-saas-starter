import { Plus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import type {
  OrganizationAdmin,
  OrganizationSearchParams,
} from "../../hooks/api/useSuperAdmin";
import {
  useCreateOrganization,
  useSuperAdminOrganizations,
  useUpdateOrganization,
} from "../../hooks/api/useSuperAdmin";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Skeleton } from "../ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";

export function TenantList() {
  const [search, setSearch] = useState("");
  const [params, setParams] = useState<OrganizationSearchParams>({
    page: 1,
    page_size: 20,
  });
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newOrgName, setNewOrgName] = useState("");
  const [newOrgSubscription, setNewOrgSubscription] = useState("trial");

  const { data, isLoading, error } = useSuperAdminOrganizations({
    ...params,
    search: search || undefined,
  });
  const updateOrg = useUpdateOrganization();
  const createOrg = useCreateOrganization();

  const handleToggleActive = async (org: OrganizationAdmin) => {
    try {
      await updateOrg.mutateAsync({
        orgId: org.id,
        data: { is_active: !org.is_active },
      });
      toast.success(
        `Organization ${org.is_active ? "suspended" : "activated"}`,
      );
    } catch {
      toast.error("Failed to update organization");
    }
  };

  const handleCreateOrganization = async () => {
    if (!newOrgName.trim()) {
      toast.error("Organization name is required");
      return;
    }
    try {
      await createOrg.mutateAsync({
        name: newOrgName.trim(),
        subscription_status: newOrgSubscription,
      });
      toast.success("Organization created successfully");
      setCreateDialogOpen(false);
      setNewOrgName("");
      setNewOrgSubscription("trial");
    } catch {
      toast.error("Failed to create organization");
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle>All Organizations</CardTitle>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <Input
              placeholder="Search organizations..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full sm:w-64"
            />
            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" className="whitespace-nowrap">
                  <Plus className="mr-1 h-4 w-4" />
                  New Organization
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Organization</DialogTitle>
                  <DialogDescription>
                    Create a new organization. You can add members afterwards.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="org-name">Organization Name</Label>
                    <Input
                      id="org-name"
                      placeholder="Enter organization name"
                      value={newOrgName}
                      onChange={(e) => setNewOrgName(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="subscription">Subscription Status</Label>
                    <Select
                      value={newOrgSubscription}
                      onValueChange={setNewOrgSubscription}
                    >
                      <SelectTrigger id="subscription">
                        <SelectValue placeholder="Select subscription" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="trial">Trial</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="past_due">Past Due</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setCreateDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreateOrganization}
                    disabled={createOrg.isPending}
                  >
                    {createOrg.isPending
                      ? "Creating..."
                      : "Create Organization"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : error ? (
          <div className="text-red-500">Failed to load organizations</div>
        ) : (
          <>
            <div className="-mx-4 overflow-x-auto sm:mx-0">
              <div className="inline-block min-w-full align-middle">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="whitespace-nowrap">Name</TableHead>
                      <TableHead className="whitespace-nowrap">
                        Members
                      </TableHead>
                      <TableHead className="whitespace-nowrap">
                        Patients
                      </TableHead>
                      <TableHead className="whitespace-nowrap">
                        Subscription
                      </TableHead>
                      <TableHead className="whitespace-nowrap">
                        Status
                      </TableHead>
                      <TableHead className="whitespace-nowrap">
                        Created
                      </TableHead>
                      <TableHead className="whitespace-nowrap">
                        Actions
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data?.items.map((org) => (
                      <TableRow key={org.id}>
                        <TableCell className="font-medium whitespace-nowrap">
                          {org.name}
                        </TableCell>
                        <TableCell>{org.member_count}</TableCell>
                        <TableCell>{org.patient_count}</TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {org.subscription_status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={org.is_active ? "default" : "destructive"}
                          >
                            {org.is_active ? "Active" : "Suspended"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm whitespace-nowrap">
                          {new Date(org.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant={org.is_active ? "destructive" : "default"}
                            onClick={() => handleToggleActive(org)}
                            disabled={updateOrg.isPending}
                          >
                            {org.is_active ? "Suspend" : "Activate"}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>

            <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between text-sm">
              <span>Total: {data?.total || 0} organizations</span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={params.page === 1}
                  onClick={() =>
                    setParams({ ...params, page: (params.page || 1) - 1 })
                  }
                >
                  Previous
                </Button>
                <span className="py-1">Page {params.page}</span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={
                    (data?.items.length || 0) < (params.page_size || 20)
                  }
                  onClick={() =>
                    setParams({ ...params, page: (params.page || 1) + 1 })
                  }
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
