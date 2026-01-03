import { useSupportTickets } from '../../hooks/api/useSupportTickets';
import type { SupportTicket } from '../../hooks/api/useSupportTickets';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Skeleton } from '../ui/skeleton';

function getStatusBadgeVariant(status: string) {
    switch (status) {
        case 'OPEN':
            return 'default';
        case 'IN_PROGRESS':
            return 'secondary';
        case 'RESOLVED':
            return 'outline';
        case 'CLOSED':
            return 'destructive';
        default:
            return 'default';
    }
}

function getPriorityBadgeVariant(priority: string) {
    switch (priority) {
        case 'HIGH':
            return 'destructive';
        case 'MEDIUM':
            return 'secondary';
        case 'LOW':
            return 'outline';
        default:
            return 'default';
    }
}

interface TicketListProps {
    onSelectTicket?: (ticket: SupportTicket) => void;
}

export function TicketList({ onSelectTicket }: TicketListProps) {
    const { data: tickets, isLoading, error } = useSupportTickets();

    if (isLoading) {
        return (
            <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                    <Skeleton key={i} className="h-24 w-full" />
                ))}
            </div>
        );
    }

    if (error) {
        return <div className="text-red-500">Failed to load tickets</div>;
    }

    if (!tickets?.length) {
        return (
            <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                    No support tickets yet. Create one to get help.
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-3">
            {tickets.map((ticket) => (
                <Card
                    key={ticket.id}
                    className="cursor-pointer hover:bg-muted/50 transition-colors"
                    onClick={() => onSelectTicket?.(ticket)}
                >
                    <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg">{ticket.subject}</CardTitle>
                            <div className="flex gap-2">
                                <Badge variant={getPriorityBadgeVariant(ticket.priority)}>
                                    {ticket.priority}
                                </Badge>
                                <Badge variant={getStatusBadgeVariant(ticket.status)}>
                                    {ticket.status}
                                </Badge>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                            <span>{ticket.category}</span>
                            <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="mt-1 text-sm text-muted-foreground">
                            {ticket.message_count} message{ticket.message_count !== 1 ? 's' : ''}
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
