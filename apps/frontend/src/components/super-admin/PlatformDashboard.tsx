import { useSystemHealth } from "../../hooks/api/useSuperAdmin";
import { Badge } from "../ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Skeleton } from "../ui/skeleton";

function StatusBadge({ status }: { status: string }) {
  const variant = status === "healthy" ? "default" : "destructive";
  return <Badge variant={variant}>{status}</Badge>;
}

export function PlatformDashboard() {
  const { data: health, isLoading: healthLoading } = useSystemHealth();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Platform Overview</h2>

      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Organizations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {health?.metrics.total_organizations ?? (
                <Skeleton className="h-9 w-16" />
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Users
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {health?.metrics.total_users ?? <Skeleton className="h-9 w-16" />}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            {healthLoading ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="flex gap-2">
                <StatusBadge status={health?.db_status || "unknown"} />
                <StatusBadge status={health?.redis_status || "unknown"} />
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          {healthLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : (
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 border rounded">
                <span>Database</span>
                <StatusBadge status={health?.db_status || "unknown"} />
              </div>
              <div className="flex items-center justify-between p-3 border rounded">
                <span>Redis</span>
                <StatusBadge status={health?.redis_status || "unknown"} />
              </div>
              <div className="flex items-center justify-between p-3 border rounded">
                <span>Worker</span>
                <StatusBadge status={health?.worker_status || "unknown"} />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
