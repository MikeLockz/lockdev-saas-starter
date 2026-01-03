import { createFileRoute } from '@tanstack/react-router';
import { AuditLogViewer } from '../../../components/admin/AuditLogViewer';

export const Route = createFileRoute('/_auth/admin/audit-logs')({
    component: AuditLogsPage,
});

function AuditLogsPage() {
    return (
        <div className="container mx-auto py-8">
            <h1 className="text-3xl font-bold mb-8">Audit Logs</h1>
            <AuditLogViewer />
        </div>
    );
}
