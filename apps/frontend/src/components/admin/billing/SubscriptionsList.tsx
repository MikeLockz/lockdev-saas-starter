import { Search } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAdminSubscriptions } from "@/hooks/api/useAdminBilling";
import { formatCurrency, formatDate } from "@/lib/utils";
import { SubscriptionActionsMenu } from "./SubscriptionActionsMenu";

export function SubscriptionsList() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [ownerTypeFilter, setOwnerTypeFilter] = useState<string>("all");

  const { data, isLoading } = useAdminSubscriptions({
    page,
    page_size: 50,
    search: search || undefined,
    status: statusFilter !== "all" ? statusFilter : undefined,
    owner_type: ownerTypeFilter !== "all" ? ownerTypeFilter : undefined,
  });

  const getStatusBadge = (status: string) => {
    const variants: Record<
      string,
      "default" | "secondary" | "destructive" | "outline"
    > = {
      ACTIVE: "default",
      TRIALING: "secondary",
      PAST_DUE: "destructive",
      CANCELED: "outline",
      CANCELLED: "outline",
    };
    return <Badge variant={variants[status] || "secondary"}>{status}</Badge>;
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="pl-9"
          />
        </div>
        <Select
          value={statusFilter}
          onValueChange={(v) => {
            setStatusFilter(v);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="ACTIVE">Active</SelectItem>
            <SelectItem value="TRIALING">Trialing</SelectItem>
            <SelectItem value="PAST_DUE">Past Due</SelectItem>
            <SelectItem value="CANCELED">Canceled</SelectItem>
          </SelectContent>
        </Select>
        <Select
          value={ownerTypeFilter}
          onValueChange={(v) => {
            setOwnerTypeFilter(v);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="PATIENT">Patients</SelectItem>
            <SelectItem value="ORGANIZATION">Organizations</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Customer</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Billing Manager</TableHead>
              <TableHead>Plan</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>MRR</TableHead>
              <TableHead>Next Billing</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              [...Array(5)].map((_, i) => (
                <TableRow key={i}>
                  <TableCell colSpan={9}>
                    <Skeleton className="h-10 w-full" />
                  </TableCell>
                </TableRow>
              ))
            ) : data?.subscriptions.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={9}
                  className="text-center py-8 text-muted-foreground"
                >
                  No subscriptions found
                </TableCell>
              </TableRow>
            ) : (
              data?.subscriptions.map((subscription) => (
                <TableRow key={subscription.owner_id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">
                        {subscription.owner_name}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {subscription.owner_email}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{subscription.owner_type}</Badge>
                  </TableCell>
                  <TableCell>
                    {subscription.billing_manager_name ? (
                      <div className="text-sm">
                        <div className="font-medium">
                          {subscription.billing_manager_name}
                        </div>
                        <div className="text-muted-foreground">Managed</div>
                      </div>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>{subscription.plan_id || "N/A"}</TableCell>
                  <TableCell>
                    {getStatusBadge(subscription.subscription_status)}
                  </TableCell>
                  <TableCell className="font-semibold">
                    {formatCurrency(subscription.mrr_cents / 100)}
                  </TableCell>
                  <TableCell>
                    {subscription.current_period_end
                      ? formatDate(new Date(subscription.current_period_end))
                      : "N/A"}
                  </TableCell>
                  <TableCell>
                    {formatDate(new Date(subscription.created_at))}
                  </TableCell>
                  <TableCell>
                    <SubscriptionActionsMenu subscription={subscription} />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {data?.subscriptions.length || 0} of {data?.total || 0}{" "}
          subscriptions
          {data && (
            <span className="ml-2 font-semibold">
              Total MRR: {formatCurrency(data.total_mrr_cents / 100)}
            </span>
          )}
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={!data || data.subscriptions.length < 50}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
