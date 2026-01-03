import { createFileRoute, Link } from '@tanstack/react-router';
import { PlatformDashboard } from '../../../components/super-admin/PlatformDashboard';
import { Button } from '../../../components/ui/button';

export const Route = createFileRoute('/_auth/super-admin/')({
    component: SuperAdminIndex,
});

function SuperAdminIndex() {
    return (
        <div className="container mx-auto py-8">
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-3xl font-bold">Super Admin Dashboard</h1>
                <div className="flex gap-4">
                    <Link to="/super-admin/organizations">
                        <Button variant="outline">Organizations</Button>
                    </Link>
                    <Link to="/super-admin/users">
                        <Button variant="outline">Users</Button>
                    </Link>
                </div>
            </div>

            <PlatformDashboard />
        </div>
    );
}
