import { useState } from 'react';
import { useCreateTicket } from '../../hooks/api/useSupportTickets';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { toast } from 'sonner';

const CATEGORIES = ['TECHNICAL', 'BILLING', 'ACCOUNT', 'OTHER'];
const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH'];

interface SupportTicketFormProps {
    onSuccess?: () => void;
}

export function SupportTicketForm({ onSuccess }: SupportTicketFormProps) {
    const [subject, setSubject] = useState('');
    const [category, setCategory] = useState('TECHNICAL');
    const [priority, setPriority] = useState('MEDIUM');
    const [message, setMessage] = useState('');

    const createTicket = useCreateTicket();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!subject.trim() || !message.trim()) {
            toast.error('Please fill in all required fields');
            return;
        }

        try {
            await createTicket.mutateAsync({
                subject,
                category,
                priority,
                initial_message: message,
            });

            toast.success('Support ticket created');
            setSubject('');
            setMessage('');
            onSuccess?.();
        } catch (error) {
            toast.error('Failed to create ticket');
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Create Support Ticket</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="subject" className="block text-sm font-medium mb-1">Subject</label>
                        <Input
                            id="subject"
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                            placeholder="Brief description of your issue"
                            required
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Category</label>
                            <Select value={category} onValueChange={setCategory}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {CATEGORIES.map((cat) => (
                                        <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">Priority</label>
                            <Select value={priority} onValueChange={setPriority}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {PRIORITIES.map((p) => (
                                        <SelectItem key={p} value={p}>{p}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div>
                        <label htmlFor="message" className="block text-sm font-medium mb-1">Message</label>
                        <Textarea
                            id="message"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Describe your issue in detail..."
                            rows={5}
                            required
                        />
                    </div>

                    <Button type="submit" disabled={createTicket.isPending}>
                        {createTicket.isPending ? 'Submitting...' : 'Submit Ticket'}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}
