import { createFileRoute } from "@tanstack/react-router";
import {
  Activity,
  CheckCircle2,
  Database,
  HardDrive,
  RefreshCw,
  Server,
  XCircle,
} from "lucide-react";
import { useState } from "react";
import { RoleGuard } from "@/components/auth/RoleGuard";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export const Route = createFileRoute("/_auth/super-admin/system")({
  component: SystemHealthPage,
});

interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  latency?: number;
  message?: string;
}

function SystemHealthPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastChecked, setLastChecked] = useState(new Date());

  // Mock system health data - in production, this would come from actual API endpoints
  const systemHealth = {
    api: { status: "healthy" as const, latency: 45 },
    database: { status: "healthy" as const, latency: 12 },
    redis: { status: "healthy" as const, latency: 3 },
    storage: { status: "healthy" as const, latency: 28 },
  };

  const systemMetrics = {
    cpuUsage: 32,
    memoryUsage: 58,
    diskUsage: 45,
    activeConnections: 127,
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setLastChecked(new Date());
    setIsRefreshing(false);
  };

  const getStatusIcon = (status: HealthStatus["status"]) => {
    switch (status) {
      case "healthy":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "degraded":
        return <Activity className="h-5 w-5 text-yellow-500" />;
      case "unhealthy":
        return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getStatusBadge = (status: HealthStatus["status"]) => {
    switch (status) {
      case "healthy":
        return <Badge className="bg-green-500">Healthy</Badge>;
      case "degraded":
        return <Badge className="bg-yellow-500">Degraded</Badge>;
      case "unhealthy":
        return <Badge variant="destructive">Unhealthy</Badge>;
    }
  };

  return (
    <RoleGuard allowedRoles={["super_admin"]}>
      <Header fixed>
        <div className="flex items-center gap-2">
          <Server className="h-5 w-5" />
          <h1 className="text-lg font-semibold">System Health</h1>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            Last checked: {lastChecked.toLocaleTimeString()}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw
              className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </Header>
      <Main>
        <div className="space-y-6">
          {/* Service Status */}
          <Card>
            <CardHeader>
              <CardTitle>Service Status</CardTitle>
              <CardDescription>
                Real-time health status of all system services
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Server className="h-8 w-8 text-muted-foreground" />
                    <div>
                      <p className="font-medium">API Server</p>
                      <p className="text-sm text-muted-foreground">
                        {systemHealth.api.latency}ms latency
                      </p>
                    </div>
                  </div>
                  {getStatusIcon(systemHealth.api.status)}
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Database className="h-8 w-8 text-muted-foreground" />
                    <div>
                      <p className="font-medium">Database</p>
                      <p className="text-sm text-muted-foreground">
                        {systemHealth.database.latency}ms latency
                      </p>
                    </div>
                  </div>
                  {getStatusIcon(systemHealth.database.status)}
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Activity className="h-8 w-8 text-muted-foreground" />
                    <div>
                      <p className="font-medium">Redis Cache</p>
                      <p className="text-sm text-muted-foreground">
                        {systemHealth.redis.latency}ms latency
                      </p>
                    </div>
                  </div>
                  {getStatusIcon(systemHealth.redis.status)}
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <HardDrive className="h-8 w-8 text-muted-foreground" />
                    <div>
                      <p className="font-medium">Storage</p>
                      <p className="text-sm text-muted-foreground">
                        {systemHealth.storage.latency}ms latency
                      </p>
                    </div>
                  </div>
                  {getStatusIcon(systemHealth.storage.status)}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Resource Usage</CardTitle>
                <CardDescription>
                  Current system resource utilization
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>CPU Usage</span>
                    <span>{systemMetrics.cpuUsage}%</span>
                  </div>
                  <Progress value={systemMetrics.cpuUsage} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Memory Usage</span>
                    <span>{systemMetrics.memoryUsage}%</span>
                  </div>
                  <Progress value={systemMetrics.memoryUsage} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Disk Usage</span>
                    <span>{systemMetrics.diskUsage}%</span>
                  </div>
                  <Progress value={systemMetrics.diskUsage} className="h-2" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Active Connections</CardTitle>
                <CardDescription>
                  Current active user sessions and connections
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center justify-center py-8">
                  <div className="text-5xl font-bold text-primary">
                    {systemMetrics.activeConnections}
                  </div>
                  <p className="text-muted-foreground mt-2">
                    Active Connections
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div className="text-center">
                    <p className="text-2xl font-semibold">98.9%</p>
                    <p className="text-sm text-muted-foreground">Uptime</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-semibold">~45ms</p>
                    <p className="text-sm text-muted-foreground">
                      Avg Response
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Overall Status Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Overall System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 p-4 bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 rounded-lg">
                <CheckCircle2 className="h-8 w-8 text-green-500" />
                <div>
                  <p className="font-semibold text-green-700 dark:text-green-400">
                    All Systems Operational
                  </p>
                  <p className="text-sm text-green-600 dark:text-green-500">
                    All services are running normally with no issues detected.
                  </p>
                </div>
                {getStatusBadge("healthy")}
              </div>
            </CardContent>
          </Card>
        </div>
      </Main>
    </RoleGuard>
  );
}
