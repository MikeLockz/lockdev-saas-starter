import { useState } from "react";
import { toast } from "sonner";
import type { AuditLogSearchParams } from "../../hooks/api/useAuditLogs";
import { exportAuditLogs, useAuditLogs } from "../../hooks/api/useAuditLogs";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Input } from "../ui/input";
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

const ACTION_TYPES = [
  "READ",
  "CREATE",
  "UPDATE",
  "DELETE",
  "IMPERSONATE",
  "EXPORT",
];
const RESOURCE_TYPES = [
  "PATIENT",
  "USER",
  "APPOINTMENT",
  "DOCUMENT",
  "ORGANIZATION",
  "AUDIT_LOG",
];

export function AuditLogViewer() {
  const [filters, setFilters] = useState<AuditLogSearchParams>({
    page: 1,
    page_size: 50,
  });

  const { data, isLoading, error } = useAuditLogs(filters);

  const handleExport = async () => {
    try {
      const response = await exportAuditLogs(filters);
      const blob = new Blob([response.data], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `audit_logs_${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Export downloaded");
    } catch {
      toast.error("Export failed");
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Audit Log Viewer</CardTitle>
            <Button onClick={handleExport} variant="outline">
              Export CSV
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Action Type
              </label>
              <Select
                value={filters.action_type || "__all__"}
                onValueChange={(v) =>
                  setFilters({
                    ...filters,
                    action_type: v === "__all__" ? undefined : v,
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__all__">All</SelectItem>
                  {ACTION_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Resource Type
              </label>
              <Select
                value={filters.resource_type || "__all__"}
                onValueChange={(v) =>
                  setFilters({
                    ...filters,
                    resource_type: v === "__all__" ? undefined : v,
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__all__">All</SelectItem>
                  {RESOURCE_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Date From
              </label>
              <Input
                type="datetime-local"
                value={filters.date_from || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    date_from: e.target.value || undefined,
                  })
                }
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Date To</label>
              <Input
                type="datetime-local"
                value={filters.date_to || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    date_to: e.target.value || undefined,
                  })
                }
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : error ? (
            <div className="text-red-500">Failed to load audit logs</div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Resource</TableHead>
                    <TableHead>Resource ID</TableHead>
                    <TableHead>Actor</TableHead>
                    <TableHead>IP Address</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data?.items.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="text-sm">
                        {new Date(log.occurred_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <span className="font-mono text-sm">
                          {log.action_type}
                        </span>
                      </TableCell>
                      <TableCell>{log.resource_type}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {log.resource_id.slice(0, 8)}...
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {log.actor_user_id?.slice(0, 8) || "System"}...
                      </TableCell>
                      <TableCell className="text-sm">
                        {log.ip_address || "-"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="mt-4 flex items-center justify-between text-sm text-muted-foreground">
                <span>Total: {data?.total || 0} entries</span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={filters.page === 1}
                    onClick={() =>
                      setFilters({ ...filters, page: (filters.page || 1) - 1 })
                    }
                  >
                    Previous
                  </Button>
                  <span className="py-1">Page {filters.page}</span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={
                      (data?.items.length || 0) < (filters.page_size || 50)
                    }
                    onClick={() =>
                      setFilters({ ...filters, page: (filters.page || 1) + 1 })
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
    </div>
  );
}
