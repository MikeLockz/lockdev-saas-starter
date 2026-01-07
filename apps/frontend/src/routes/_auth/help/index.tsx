import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';

export const Route = createFileRoute('/_auth/help/')({
    component: HelpIndex,
});

function HelpIndex() {
    const navigate = useNavigate();

    return (
        <div className="container mx-auto py-8">
            <h1 className="text-3xl font-bold mb-8">Help Center</h1>

            <div className="grid md:grid-cols-2 gap-6">
                <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate({ to: '/help/contact' })}>
                    <CardHeader>
                        <CardTitle>Contact Support</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-muted-foreground mb-4">
                            Need help? Create a support ticket and our team will get back to you.
                        </p>
                        <Button>Submit a Ticket</Button>
                    </CardContent>
                </Card>

                <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate({ to: '/help/tickets' })}>
                    <CardHeader>
                        <CardTitle>My Tickets</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-muted-foreground mb-4">
                            View and manage your existing support tickets.
                        </p>
                        <Button variant="outline">View Tickets</Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
