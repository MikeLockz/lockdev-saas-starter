import {
  createFileRoute,
  Outlet,
  useLocation,
  useNavigate,
} from "@tanstack/react-router";
import { Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { ComposeModal } from "@/components/messages/ComposeModal";
import { ThreadList } from "@/components/messages/ThreadList";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useThreads } from "@/hooks/api/useMessaging";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_auth/messages")({
  component: MessagesLayout,
});

type FilterType = "all" | "unread" | "archived";

function MessagesLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { data, isLoading } = useThreads();
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filter, setFilter] = useState<FilterType>("all");

  const threads = data?.items || [];

  // Filter threads based on search and filter type
  const filteredThreads = useMemo(() => {
    let result = threads;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (thread) =>
          thread.subject?.toLowerCase().includes(query) ||
          thread.last_message?.body?.toLowerCase().includes(query) ||
          thread.last_message?.sender_name?.toLowerCase().includes(query),
      );
    }

    // Apply filter tabs
    switch (filter) {
      case "unread":
        result = result.filter((thread) => thread.unread_count > 0);
        break;
      case "archived":
        result = result.filter((thread) => thread.is_archived);
        break;
      default:
        // Show all non-archived by default
        result = result.filter((thread) => !thread.is_archived);
        break;
    }

    return result;
  }, [threads, searchQuery, filter]);

  const isIndex =
    location.pathname === "/messages" || location.pathname === "/messages/";

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Sidebar - Thread List */}
      <div
        className={cn(
          "w-full md:w-80 border-r flex flex-col bg-background",
          !isIndex && "hidden md:flex",
        )}
      >
        <div className="p-4 border-b flex items-center justify-between bg-card">
          <h2 className="font-semibold text-lg">Messages</h2>
          <Button
            size="icon"
            variant="ghost"
            onClick={() => setIsComposeOpen(true)}
          >
            <Plus className="h-5 w-5" />
          </Button>
        </div>

        {/* Search Input */}
        <div className="p-3 border-b">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search messages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="px-3 py-2 border-b">
          <Tabs
            value={filter}
            onValueChange={(v) => setFilter(v as FilterType)}
          >
            <TabsList className="w-full">
              <TabsTrigger value="all" className="flex-1">
                All
              </TabsTrigger>
              <TabsTrigger value="unread" className="flex-1">
                Unread
              </TabsTrigger>
              <TabsTrigger value="archived" className="flex-1">
                Archived
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="flex-1 overflow-y-auto">
          <ThreadList
            threads={filteredThreads}
            isLoading={isLoading}
            selectedId={location.pathname.split("/").pop()}
            onSelect={(id) => navigate({ to: `/messages/${id}` })}
          />
        </div>
      </div>

      {/* Main Content - Chat Interface or Empty State */}
      <div
        className={cn(
          "flex-1 flex flex-col min-w-0 bg-muted/5",
          isIndex && "hidden md:flex",
        )}
      >
        <Outlet />
      </div>

      <ComposeModal
        open={isComposeOpen}
        onOpenChange={setIsComposeOpen}
        defaultOrganizationId={threads[0]?.organization_id}
        onSuccess={(threadId) => navigate({ to: `/messages/${threadId}` })}
      />
    </div>
  );
}
