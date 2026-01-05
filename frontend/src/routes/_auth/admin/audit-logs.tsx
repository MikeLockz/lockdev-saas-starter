import { createFileRoute } from '@tanstack/react-router';
import { Header } from '@/components/layout/header';
import { Main } from '@/components/layout/main';
import { AuditLogViewer } from '../../../components/admin/AuditLogViewer';

export const Route = createFileRoute('/_auth/admin/audit-logs')({
    component: AuditLogsPage,
});

function AuditLogsPage() {
    return (
        <>
            <Header fixed>
                <h1 className="text-lg font-semibold">Audit Logs</h1>
            </Header>
            <Main>
                <AuditLogViewer />
            </Main>
        </>
    );
}
