import { useState } from 'react';
import { useSuperAdminOrganizations, useUpdateOrganization } from '../../hooks/api/useSuperAdmin';
import type { OrganizationAdmin, OrganizationSearchParams } from '../../hooks/api/useSuperAdmin';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Skeleton } from '../ui/skeleton';
import { toast } from 'sonner';

export function TenantList() {
    const [search, setSearch] = useState('');
    const [params, setParams] = useState<OrganizationSearchParams>({ page: 1, page_size: 20 });

    const { data, isLoading, error } = useSuperAdminOrganizations({ ...params, search: search || undefined });
    const updateOrg = useUpdateOrganization();

    const handleToggleActive = async (org: OrganizationAdmin) => {
        try {
            await updateOrg.mutateAsync({ orgId: org.id, data: { is_active: !org.is_active } });
            toast.success(`Organization ${org.is_active ? 'suspended' : 'activated'}`);
        } catch {
            toast.error('Failed to update organization');
        }
    };

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle>All Organizations</CardTitle>
                    <Input
                        placeholder="Search organizations..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="max-w-xs"
                    />
                </div>
            </CardHeader>
            <CardContent>
                {isLoading ? (
                    <div className="space-y-2">
                        {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
                    </div>
                ) : error ? (
                    <div className="text-red-500">Failed to load organizations</div>
                ) : (
                    <>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Members</TableHead>
                                    <TableHead>Patients</TableHead>
                                    <TableHead>Subscription</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Created</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data?.items.map((org) => (
                                    <TableRow key={org.id}>
                                        <TableCell className="font-medium">{org.name}</TableCell>
                                        <TableCell>{org.member_count}</TableCell>
                                        <TableCell>{org.patient_count}</TableCell>
                                        <TableCell>
                                            <Badge variant="outline">{org.subscription_status}</Badge>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant={org.is_active ? 'default' : 'destructive'}>
                                                {org.is_active ? 'Active' : 'Suspended'}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-sm">
                                            {new Date(org.created_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell>
                                            <Button
                                                size="sm"
                                                variant={org.is_active ? 'destructive' : 'default'}
                                                onClick={() => handleToggleActive(org)}
                                                disabled={updateOrg.isPending}
                                            >
                                                {org.is_active ? 'Suspend' : 'Activate'}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>

                        <div className="mt-4 flex items-center justify-between text-sm">
                            <span>Total: {data?.total || 0} organizations</span>
                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    disabled={params.page === 1}
                                    onClick={() => setParams({ ...params, page: (params.page || 1) - 1 })}
                                >
                                    Previous
                                </Button>
                                <span className="py-1">Page {params.page}</span>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    disabled={(data?.items.length || 0) < (params.page_size || 20)}
                                    onClick={() => setParams({ ...params, page: (params.page || 1) + 1 })}
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
