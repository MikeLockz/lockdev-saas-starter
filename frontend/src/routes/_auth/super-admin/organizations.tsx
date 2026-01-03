import { createFileRoute, Link } from '@tanstack/react-router';
import { TenantList } from '../../../components/super-admin/TenantList';
import { Button } from '../../../components/ui/button';

export const Route = createFileRoute('/_auth/super-admin/organizations')({
    component: OrganizationsPage,
});

function OrganizationsPage() {
    return (
        <div className="container mx-auto py-8">
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-3xl font-bold">Organizations</h1>
                <Link to="/super-admin">
                    <Button variant="outline">← Back to Dashboard</Button>
                </Link>
            </div>

            <TenantList />
        </div>
    );
}
