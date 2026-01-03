import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import type { Thread } from "@/hooks/api/useMessaging";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { User, MessageSquare } from "lucide-react";

interface ThreadListProps {
    threads: Thread[];
    isLoading: boolean;
    selectedId?: string;
    onSelect: (id: string) => void;
}

export function ThreadList({ threads, isLoading, selectedId, onSelect }: ThreadListProps) {
    if (isLoading) {
        return (
            <div className="space-y-2 p-2">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="flex gap-3 p-3 border rounded-lg">
                        <Skeleton className="h-10 w-10 rounded-full" />
                        <div className="space-y-2 flex-1">
                            <Skeleton className="h-4 w-1/2" />
                            <Skeleton className="h-3 w-3/4" />
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    if (threads.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-48 text-muted-foreground p-4 text-center">
                <MessageSquare className="h-8 w-8 mb-2 opacity-50" />
                <p className="text-sm">No messages yet</p>
            </div>
        );
    }

    return (
        <div className="space-y-1 p-2">
            {threads.map((thread) => (
                <button
                    key={thread.id}
                    onClick={() => onSelect(thread.id)}
                    className={cn(
                        "w-full text-left flex gap-3 p-3 rounded-lg transition-colors hover:bg-muted/50",
                        selectedId === thread.id && "bg-muted",
                        thread.unread_count > 0 && "bg-blue-50/50 dark:bg-blue-950/20"
                    )}
                >
                    <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center shrink-0">
                        <User className="h-5 w-5 text-muted-foreground" />
                    </div>

                    <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start mb-0.5">
                            <span className={cn("font-medium text-sm truncate", thread.unread_count > 0 && "font-semibold")}>
                                {thread.subject}
                            </span>
                            <span className="text-[10px] text-muted-foreground shrink-0 ml-2">
                                {formatDistanceToNow(new Date(thread.updated_at), { addSuffix: false })}
                            </span>
                        </div>

                        <div className="flex justify-between items-end">
                            <p className="text-xs text-muted-foreground truncate pr-2 max-w-[80%]">
                                {thread.last_message ? (
                                    <>
                                        <span className="font-medium text-foreground/80">{thread.last_message.sender_name || "Unknown"}: </span>
                                        {thread.last_message.body}
                                    </>
                                ) : (
                                    "No messages"
                                )}
                            </p>
                            {thread.unread_count > 0 && (
                                <Badge variant="default" className="h-5 w-5 p-0 flex items-center justify-center rounded-full text-[10px]">
                                    {thread.unread_count}
                                </Badge>
                            )}
                        </div>
                    </div>
                </button>
            ))}
        </div>
    );
}
