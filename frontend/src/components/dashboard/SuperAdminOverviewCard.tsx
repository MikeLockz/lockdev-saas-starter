import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { useSystemHealth, useSuperAdminOrganizations, useSuperAdminUsers } from '@/hooks/api/useSuperAdmin';
import { Shield, Building2, Users, Server, Database, Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Link } from '@tanstack/react-router';

/**
 * Super Admin Overview Card displays:
 * - Platform-wide metrics (total orgs, users)
 * - System health indicators (DB, Redis, Worker)
 * - Active organizations summary
 * - Quick links to super admin management pages
 */
export function SuperAdminOverviewCard() {
    const { data: systemHealth, isLoading: isHealthLoading } = useSystemHealth();
    const { data: orgsData, isLoading: isOrgsLoading } = useSuperAdminOrganizations({ page_size: 5 });
    const { data: usersData, isLoading: isUsersLoading } = useSuperAdminUsers({ is_locked: true, page_size: 10 });

    const isLoading = isHealthLoading || isOrgsLoading || isUsersLoading;

    const getStatusColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'healthy':
            case 'connected':
            case 'ok':
                return 'default';
            case 'degraded':
            case 'warning':
            case 'no_workers':
            case 'not_configured':
                return 'secondary';
            case 'unhealthy':
            case 'error':
            case 'disconnected':
                return 'destructive';
            default:
                return 'outline';
        }
    };

    const getStatusIcon = (status: string) => {
        const lower = status?.toLowerCase();
        if (['healthy', 'connected', 'ok'].includes(lower)) {
            return <CheckCircle2 className="h-3 w-3" />;
        }
        return <AlertTriangle className="h-3 w-3" />;
    };

    const getWorkerStatusLabel = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'healthy':
                return 'Healthy';
            case 'unhealthy':
                return 'Unhealthy';
            case 'no_workers':
                return 'No Workers';
            case 'not_configured':
                return 'Not Configured';
            case 'unknown':
                return 'Unknown';
            default:
                return status || 'Unknown';
        }
    };

    const lockedUsersCount = usersData?.total || 0;

    if (isLoading) {
        return (
            <Card className="lg:col-span-4">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        Platform Overview
                    </CardTitle>
                    <CardDescription>Loading platform metrics...</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="flex items-center gap-4">
                            <Skeleton className="h-10 w-16" />
                            <div className="flex-1 space-y-1">
                                <Skeleton className="h-4 w-32" />
                                <Skeleton className="h-3 w-24" />
                            </div>
                        </div>
                    ))}
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="lg:col-span-4">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <Shield className="h-5 w-5" />
                            Platform Overview
                        </CardTitle>
                        <CardDescription>
                            {systemHealth?.metrics.total_organizations || 0} organizations · {systemHealth?.metrics.total_users || 0} users
                        </CardDescription>
                    </div>
                    {lockedUsersCount > 0 && (
                        <Badge variant="destructive" className="flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            {lockedUsersCount} locked
                        </Badge>
                    )}
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {/* System Health Section */}
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                            <Server className="h-4 w-4" />
                            System Health
                        </h4>
                        <div className="grid grid-cols-3 gap-3">
                            <div className="flex flex-col items-center gap-1 p-3 rounded-md bg-muted/50">
                                <Database className="h-5 w-5 text-muted-foreground" />
                                <span className="text-xs text-muted-foreground">Database</span>
                                <Badge variant={getStatusColor(systemHealth?.db_status || '')} className="text-xs flex items-center gap-1">
                                    {getStatusIcon(systemHealth?.db_status || '')}
                                    {systemHealth?.db_status || 'Unknown'}
                                </Badge>
                            </div>
                            <div className="flex flex-col items-center gap-1 p-3 rounded-md bg-muted/50">
                                <Activity className="h-5 w-5 text-muted-foreground" />
                                <span className="text-xs text-muted-foreground">Redis</span>
                                <Badge variant={getStatusColor(systemHealth?.redis_status || '')} className="text-xs flex items-center gap-1">
                                    {getStatusIcon(systemHealth?.redis_status || '')}
                                    {systemHealth?.redis_status || 'Unknown'}
                                </Badge>
                            </div>
                            <div className="flex flex-col items-center gap-1 p-3 rounded-md bg-muted/50">
                                <Server className="h-5 w-5 text-muted-foreground" />
                                <span className="text-xs text-muted-foreground">Worker</span>
                                <Badge variant={getStatusColor(systemHealth?.worker_status || '')} className="text-xs flex items-center gap-1">
                                    {getStatusIcon(systemHealth?.worker_status || '')}
                                    {getWorkerStatusLabel(systemHealth?.worker_status || '')}
                                </Badge>
                            </div>
                        </div>
                    </div>

                    {/* Platform Metrics Section */}
                    <div className="pt-3 border-t space-y-3">
                        <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                            <Building2 className="h-4 w-4" />
                            Platform Metrics
                        </h4>
                        <div className="grid grid-cols-2 gap-3">
                            <Link
                                to="/super-admin/organizations"
                                className="p-3 rounded-md bg-muted/30 border border-muted hover:bg-muted/50 transition-colors"
                            >
                                <div className="flex items-center gap-2">
                                    <Building2 className="h-4 w-4 text-primary" />
                                    <span className="text-2xl font-bold">{systemHealth?.metrics.total_organizations || 0}</span>
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">Total Organizations</p>
                            </Link>
                            <Link
                                to="/super-admin/users"
                                className="p-3 rounded-md bg-muted/30 border border-muted hover:bg-muted/50 transition-colors"
                            >
                                <div className="flex items-center gap-2">
                                    <Users className="h-4 w-4 text-primary" />
                                    <span className="text-2xl font-bold">{systemHealth?.metrics.total_users || 0}</span>
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">Total Users</p>
                            </Link>
                        </div>
                    </div>

                    {/* Recent Organizations Section */}
                    {orgsData && orgsData.items.length > 0 && (
                        <div className="pt-3 border-t space-y-2">
                            <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                <Building2 className="h-4 w-4" />
                                Recent Organizations
                            </h4>
                            <div className="space-y-2">
                                {orgsData.items.slice(0, 3).map((org) => (
                                    <div
                                        key={org.id}
                                        className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/30 hover:bg-muted/50 transition-colors"
                                    >
                                        <div className="flex items-center gap-2 min-w-0">
                                            <Building2 className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                                            <span className="text-sm font-medium truncate">{org.name}</span>
                                        </div>
                                        <div className="flex items-center gap-2 flex-shrink-0">
                                            <span className="text-xs text-muted-foreground">
                                                {org.member_count} members
                                            </span>
                                            <Badge variant={org.is_active ? 'default' : 'secondary'} className="text-xs">
                                                {org.is_active ? 'Active' : 'Inactive'}
                                            </Badge>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            {orgsData.total > 3 && (
                                <Link
                                    to="/super-admin/organizations"
                                    className="text-xs text-primary hover:underline block text-center pt-1"
                                >
                                    View all {orgsData.total} organizations →
                                </Link>
                            )}
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
