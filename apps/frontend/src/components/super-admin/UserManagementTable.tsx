import { useState } from 'react';
import { useSuperAdminUsers, useUnlockUser, useUpdateUserAdmin } from '../../hooks/api/useSuperAdmin';
import type { UserAdmin, UserSearchParams } from '../../hooks/api/useSuperAdmin';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Skeleton } from '../ui/skeleton';
import { toast } from 'sonner';

export function UserManagementTable() {
    const [search, setSearch] = useState('');
    const [params, setParams] = useState<UserSearchParams>({ page: 1, page_size: 20 });

    const { data, isLoading, error } = useSuperAdminUsers({ ...params, search: search || undefined });
    const unlockUser = useUnlockUser();
    const updateUser = useUpdateUserAdmin();

    const handleUnlock = async (user: UserAdmin) => {
        try {
            await unlockUser.mutateAsync(user.id);
            toast.success(`User ${user.email} unlocked`);
        } catch {
            toast.error('Failed to unlock user');
        }
    };

    const handleToggleSuperAdmin = async (user: UserAdmin) => {
        try {
            await updateUser.mutateAsync({ userId: user.id, data: { is_super_admin: !user.is_super_admin } });
            toast.success(`User ${user.is_super_admin ? 'demoted' : 'promoted to super admin'}`);
        } catch {
            toast.error('Failed to update user');
        }
    };

    const isLocked = (user: UserAdmin) => {
        return user.locked_until && new Date(user.locked_until) > new Date();
    };

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle>All Users</CardTitle>
                    <Input
                        placeholder="Search by email..."
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
                    <div className="text-red-500">Failed to load users</div>
                ) : (
                    <>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Email</TableHead>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Role</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Last Login</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data?.items.map((user) => (
                                    <TableRow key={user.id}>
                                        <TableCell className="font-medium">{user.email}</TableCell>
                                        <TableCell>{user.display_name || '-'}</TableCell>
                                        <TableCell>
                                            {user.is_super_admin && <Badge variant="secondary">Super Admin</Badge>}
                                        </TableCell>
                                        <TableCell>
                                            {isLocked(user) ? (
                                                <Badge variant="destructive">Locked</Badge>
                                            ) : (
                                                <Badge variant="default">Active</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-sm">
                                            {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : 'Never'}
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex gap-2">
                                                {isLocked(user) && (
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => handleUnlock(user)}
                                                        disabled={unlockUser.isPending}
                                                    >
                                                        Unlock
                                                    </Button>
                                                )}
                                                <Button
                                                    size="sm"
                                                    variant={user.is_super_admin ? 'destructive' : 'secondary'}
                                                    onClick={() => handleToggleSuperAdmin(user)}
                                                    disabled={updateUser.isPending}
                                                >
                                                    {user.is_super_admin ? 'Revoke Admin' : 'Make Admin'}
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>

                        <div className="mt-4 flex items-center justify-between text-sm">
                            <span>Total: {data?.total || 0} users</span>
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
