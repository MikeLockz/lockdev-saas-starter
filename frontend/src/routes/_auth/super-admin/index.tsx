import { createFileRoute, Link } from '@tanstack/react-router';
import { PlatformDashboard } from '../../../components/super-admin/PlatformDashboard';
import { Button } from '../../../components/ui/button';
import { Header } from '@/components/layout/header';
import { Main } from '@/components/layout/main';

export const Route = createFileRoute('/_auth/super-admin/')({
    component: SuperAdminIndex,
});

function SuperAdminIndex() {
    return (
        <>
            <Header fixed>
                <div className="flex items-center justify-between w-full">
                    <h1 className="text-lg font-semibold">Super Admin Dashboard</h1>
                    <div className="flex gap-4">
                        <Link to="/super-admin/organizations">
                            <Button variant="outline" size="sm">Organizations</Button>
                        </Link>
                        <Link to="/super-admin/users">
                            <Button variant="outline" size="sm">Users</Button>
                        </Link>
                    </div>
                </div>
            </Header>
            <Main>
                <PlatformDashboard />
            </Main>
        </>
    );
}
