import { createFileRoute } from "@tanstack/react-router";
import { NotificationList } from "@/components/notifications/NotificationList";

export const Route = createFileRoute("/_auth/notifications")({
    component: NotificationsPage,
});

function NotificationsPage() {
    return (
        <div className="container py-8 max-w-4xl mx-auto space-y-6">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
                <p className="text-muted-foreground">
                    Stay updated with your appointments, messages, and system alerts.
                </p>
            </div>

            <NotificationList />
        </div>
    );
}
