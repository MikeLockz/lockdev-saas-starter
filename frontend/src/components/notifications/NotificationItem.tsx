import { formatDistanceToNow } from "date-fns";
import {
    Calendar,
    MessageSquare,
    CreditCard,
    Info
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { Notification } from "@/hooks/api/useNotifications";

interface NotificationItemProps {
    notification: Notification;
    onRead?: (id: string) => void;
    onDelete?: (id: string) => void;
    compact?: boolean;
}

export function NotificationItem({
    notification,
    onRead,
    onDelete,
    compact = false
}: NotificationItemProps) {
    const Icon = getIcon(notification.type);

    return (
        <div
            className={cn(
                "relative flex gap-4 p-4 border-b hover:bg-muted/50 transition-colors",
                !notification.is_read && "bg-muted/20",
                compact && "p-3 gap-3"
            )}
        >
            <div className={cn(
                "h-10 w-10 rounded-full flex items-center justify-center shrink-0",
                getIconColor(notification.type),
                compact && "h-8 w-8"
            )}>
                <Icon className={cn("h-5 w-5", compact && "h-4 w-4")} />
            </div>

            <div className="flex-1 space-y-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                    <p className={cn("font-medium text-sm truncate", !notification.is_read && "font-semibold")}>
                        {notification.title}
                    </p>
                    <span className="text-xs text-muted-foreground whitespace-nowrap shrink-0">
                        {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                    </span>
                </div>

                <p className={cn("text-sm text-muted-foreground line-clamp-2", compact && "line-clamp-1 text-xs")}>
                    {notification.body}
                </p>

                {!compact && (
                    <div className="flex gap-2 pt-2">
                        {!notification.is_read && onRead && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2 text-xs"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onRead(notification.id);
                                }}
                            >
                                Mark as read
                            </Button>
                        )}
                        {onDelete && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2 text-xs text-destructive hover:text-destructive"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDelete(notification.id);
                                }}
                            >
                                Delete
                            </Button>
                        )}
                    </div>
                )}
            </div>

            {!notification.is_read && compact && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2 h-2 w-2 rounded-full bg-primary" />
            )}
        </div>
    );
}

function getIcon(type: Notification["type"]) {
    switch (type) {
        case "APPOINTMENT":
            return Calendar;
        case "MESSAGE":
            return MessageSquare;
        case "BILLING":
            return CreditCard;
        case "SYSTEM":
        default:
            return Info;
    }
}

function getIconColor(type: Notification["type"]) {
    switch (type) {
        case "APPOINTMENT":
            return "bg-blue-100 text-blue-600 dark:bg-blue-900/50 dark:text-blue-400";
        case "MESSAGE":
            return "bg-green-100 text-green-600 dark:bg-green-900/50 dark:text-green-400";
        case "BILLING":
            return "bg-amber-100 text-amber-600 dark:bg-amber-900/50 dark:text-amber-400";
        case "SYSTEM":
        default:
            return "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
    }
}
