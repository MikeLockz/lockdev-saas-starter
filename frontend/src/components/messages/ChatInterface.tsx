import { useRef, useEffect, useState } from "react";
import { useThread, useSendMessage, useMarkThreadRead } from "@/hooks/api/useMessaging";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Send, User as UserIcon } from "lucide-react";
import { formatRelativeTime } from "@/lib/timezone";
import { useTimezoneContext } from "@/contexts/TimezoneContext";
import { cn } from "@/lib/utils";
import { useCurrentUser } from "@/hooks/api/useCurrentUser";

interface ChatInterfaceProps {
    threadId: string;
}

export function ChatInterface({ threadId }: ChatInterfaceProps) {
    const timezone = useTimezoneContext();
    const { data: user } = useCurrentUser();
    const { data: thread, isLoading } = useThread(threadId);
    const sendMessage = useSendMessage();
    const markRead = useMarkThreadRead();
    const [message, setMessage] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [thread?.messages, isLoading]); // Scroll on load and new messages

    // Mark read on load
    useEffect(() => {
        if (threadId && thread?.unread_count && thread.unread_count > 0) {
            markRead.mutate(threadId);
        }
    }, [threadId, thread?.unread_count]);

    const handleSend = (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim()) return;

        sendMessage.mutate(
            { threadId, data: { body: message } },
            {
                onSuccess: () => setMessage(""),
            }
        );
    };

    if (isLoading) {
        return (
            <div className="flex flex-col h-full">
                <div className="p-4 border-b">
                    <Skeleton className="h-6 w-1/3" />
                </div>
                <div className="flex-1 p-4 space-y-4">
                    <Skeleton className="h-12 w-2/3" />
                    <Skeleton className="h-12 w-2/3 ml-auto" />
                    <Skeleton className="h-12 w-2/3" />
                </div>
            </div>
        );
    }

    if (!thread) {
        return <div className="flex items-center justify-center h-full">Thread not found</div>;
    }

    // Determine other participants name
    const otherParticipants = thread.participants
        .filter(p => p.user_id !== user?.id)
        .map(p => p.user_name || "Unknown")
        .join(", ");

    return (
        <div className="flex flex-col h-full bg-background rounded-lg border shadow-sm overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b flex justify-between items-center bg-card">
                <div>
                    <h3 className="font-semibold">{thread.subject}</h3>
                    <p className="text-xs text-muted-foreground">
                        {otherParticipants}
                    </p>
                </div>
            </div>

            {/* Messages */}
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/10 min-h-0"
            >
                {thread.messages?.map((msg) => {
                    const isMe = msg.sender_id === user?.id;
                    return (
                        <div
                            key={msg.id}
                            className={cn(
                                "flex gap-3 max-w-[80%]",
                                isMe ? "ml-auto flex-row-reverse" : ""
                            )}
                        >
                            <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                                <UserIcon className="h-4 w-4 text-muted-foreground" />
                            </div>

                            <div className={cn(
                                "space-y-1",
                                isMe ? "items-end" : "items-start"
                            )}>
                                <div className={cn(
                                    "flex items-center gap-2 text-xs text-muted-foreground",
                                    isMe && "flex-row-reverse"
                                )}>
                                    <span className="font-medium">{msg.sender_name || "Unknown"}</span>
                                    <span>{formatRelativeTime(msg.created_at, timezone)}</span>
                                </div>

                                <div className={cn(
                                    "p-3 rounded-lg text-sm",
                                    isMe ? "bg-primary text-primary-foreground rounded-tr-none" : "bg-muted rounded-tl-none"
                                )}>
                                    {msg.body}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Input */}
            <div className="p-4 border-t bg-card">
                <form onSubmit={handleSend} className="flex gap-2">
                    <Input
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1"
                        disabled={sendMessage.isPending}
                    />
                    <Button type="submit" size="icon" disabled={sendMessage.isPending || !message.trim()}>
                        <Send className="h-4 w-4" />
                    </Button>
                </form>
            </div>
        </div>
    );
}
