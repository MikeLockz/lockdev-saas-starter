import { createFileRoute } from "@tanstack/react-router";
import { MessageSquare } from "lucide-react";

export const Route = createFileRoute("/_auth/messages/")({
    component: MessagesIndex,
});

function MessagesIndex() {
    return (
        <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8 text-center bg-muted/10">
            <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-4">
                <MessageSquare className="h-8 w-8 opacity-50" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Select a conversation</h3>
            <p className="max-w-xs">
                Choose a thread from the sidebar or start a new message.
            </p>
        </div>
    );
}
