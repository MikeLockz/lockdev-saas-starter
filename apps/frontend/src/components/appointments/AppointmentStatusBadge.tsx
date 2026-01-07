import { Badge } from '@/components/ui/badge';

export type AppointmentStatus = 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW';

interface AppointmentStatusBadgeProps {
    status: string;
}

const statusConfig: Record<AppointmentStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
    SCHEDULED: { label: 'Scheduled', variant: 'default' },
    CONFIRMED: { label: 'Confirmed', variant: 'secondary' },
    CANCELLED: { label: 'Cancelled', variant: 'destructive' },
    COMPLETED: { label: 'Completed', variant: 'outline' },
    NO_SHOW: { label: 'No Show', variant: 'destructive' },
};

export function AppointmentStatusBadge({ status }: AppointmentStatusBadgeProps) {
    const config = statusConfig[status as AppointmentStatus] || { label: status, variant: 'outline' as const };

    return (
        <Badge variant={config.variant} className={getStatusClassName(status)}>
            {config.label}
        </Badge>
    );
}

function getStatusClassName(status: string): string {
    switch (status) {
        case 'SCHEDULED':
            return 'bg-blue-100 text-blue-800 hover:bg-blue-100';
        case 'CONFIRMED':
            return 'bg-green-100 text-green-800 hover:bg-green-100';
        case 'CANCELLED':
            return 'bg-red-100 text-red-800 hover:bg-red-100';
        case 'COMPLETED':
            return 'bg-gray-100 text-gray-800 hover:bg-gray-100';
        case 'NO_SHOW':
            return 'bg-amber-100 text-amber-800 hover:bg-amber-100';
        default:
            return '';
    }
}
