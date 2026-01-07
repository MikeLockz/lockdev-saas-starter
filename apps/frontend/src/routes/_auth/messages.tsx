import { createFileRoute, Outlet, useNavigate, useLocation } from "@tanstack/react-router";
import { useState } from "react";
import { ThreadList } from "@/components/messages/ThreadList";
import { ComposeModal } from "@/components/messages/ComposeModal";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useThreads } from "@/hooks/api/useMessaging";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_auth/messages")({
    component: MessagesLayout,
});

function MessagesLayout() {
    const navigate = useNavigate();
    const location = useLocation();
    const { data, isLoading } = useThreads();
    const [isComposeOpen, setIsComposeOpen] = useState(false);
    const threads = data?.items || [];

    // Simple desktop/mobile split logic
    // On mobile, if we are on a specific thread (location.pathname != /messages), hide the list?
    // But CSS is better. 

    const isIndex = location.pathname === "/messages" || location.pathname === "/messages/";

    return (
        <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
            {/* Sidebar - Thread List */}
            <div className={cn(
                "w-full md:w-80 border-r flex flex-col bg-background",
                !isIndex && "hidden md:flex" // Hide on mobile if viewing thread
            )}>
                <div className="p-4 border-b flex items-center justify-between bg-card">
                    <h2 className="font-semibold text-lg">Messages</h2>
                    <Button size="icon" variant="ghost" onClick={() => setIsComposeOpen(true)}>
                        <Plus className="h-5 w-5" />
                    </Button>
                </div>

                <div className="flex-1 overflow-y-auto">
                    <ThreadList
                        threads={threads}
                        isLoading={isLoading}
                        selectedId={location.pathname.split("/").pop()} // Rough check
                        onSelect={(id) => navigate({ to: `/messages/${id}` })}
                    />
                </div>
            </div>

            {/* Main Content - Chat Interface or Empty State */}
            <div className={cn(
                "flex-1 flex flex-col min-w-0 bg-muted/5",
                isIndex && "hidden md:flex" // Hide on mobile if on index (list view)
            )}>
                <Outlet />
            </div>

            <ComposeModal
                open={isComposeOpen}
                onOpenChange={setIsComposeOpen}
                defaultOrganizationId={threads[0]?.organization_id} // Fallback/Hack: use first thread org? 
                // Ideally prompt or use context. 
                onSuccess={(threadId) => navigate({ to: `/messages/${threadId}` })}
            />
        </div>
    );
}
