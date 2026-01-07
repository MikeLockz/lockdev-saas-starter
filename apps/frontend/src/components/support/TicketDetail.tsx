import { useState } from 'react';
import { useSupportTicket, useAddMessage } from '../../hooks/api/useSupportTickets';
import type { SupportMessage } from '../../hooks/api/useSupportTickets';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Skeleton } from '../ui/skeleton';
import { toast } from 'sonner';

interface TicketDetailProps {
    ticketId: string;
}

export function TicketDetail({ ticketId }: TicketDetailProps) {
    const { data: ticket, isLoading, error } = useSupportTicket(ticketId);
    const addMessage = useAddMessage(ticketId);
    const [newMessage, setNewMessage] = useState('');

    if (isLoading) {
        return <Skeleton className="h-96 w-full" />;
    }

    if (error || !ticket) {
        return <div className="text-red-500">Failed to load ticket</div>;
    }

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        try {
            await addMessage.mutateAsync({ body: newMessage });
            setNewMessage('');
            toast.success('Message sent');
        } catch {
            toast.error('Failed to send message');
        }
    };

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>{ticket.subject}</CardTitle>
                        <div className="flex gap-2">
                            <Badge>{ticket.priority}</Badge>
                            <Badge variant="outline">{ticket.status}</Badge>
                        </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                        Category: {ticket.category} • Created: {new Date(ticket.created_at).toLocaleString()}
                    </div>
                </CardHeader>
            </Card>

            <div className="space-y-3">
                {ticket.messages.map((msg: SupportMessage) => (
                    <Card key={msg.id} className={msg.is_internal ? 'border-yellow-500 bg-yellow-50' : ''}>
                        <CardContent className="py-3">
                            <div className="text-sm whitespace-pre-wrap">{msg.body}</div>
                            <div className="mt-2 text-xs text-muted-foreground">
                                {new Date(msg.created_at).toLocaleString()}
                                {msg.is_internal && <Badge variant="outline" className="ml-2">Internal</Badge>}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {ticket.status !== 'CLOSED' && (
                <form onSubmit={handleSendMessage} className="space-y-2">
                    <Textarea
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type your reply..."
                        rows={3}
                    />
                    <Button type="submit" disabled={addMessage.isPending || !newMessage.trim()}>
                        {addMessage.isPending ? 'Sending...' : 'Send Reply'}
                    </Button>
                </form>
            )}
        </div>
    );
}
