import { Link } from "@tanstack/react-router";
import {
  AlertTriangle,
  ArrowRight,
  CheckSquare,
  ClipboardList,
  Clock,
  Search,
} from "lucide-react";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useProviderPendingTasks } from "@/hooks/api/useDashboardStats";

interface StaffOverviewCardProps {
  /** Staff profile ID (currently unused but passed for future features) */
  staffId?: string | undefined;
  userId: string | undefined;
  jobTitle?: string | null;
  department?: string | null;
}

/**
 * Staff Overview Card displays:
 * - Assigned tasks queue (pending approvals, follow-ups)
 * - Quick patient search widget
 * - Role-specific summary (job title, department)
 */
export function StaffOverviewCard({
  userId,
  jobTitle,
  department,
}: StaffOverviewCardProps) {
  const { data: tasks, isLoading: isTasksLoading } =
    useProviderPendingTasks(userId);
  const [searchQuery, setSearchQuery] = useState("");

  const isLoading = isTasksLoading;

  // Count urgent/high priority tasks
  const urgentTaskCount =
    tasks?.filter((t) => t.priority === "URGENT" || t.priority === "HIGH")
      .length || 0;
  const totalPendingTasks = tasks?.length || 0;

  // Group tasks by priority
  const urgentTasks = tasks?.filter((t) => t.priority === "URGENT") || [];
  const highTasks = tasks?.filter((t) => t.priority === "HIGH") || [];
  const normalTasks =
    tasks?.filter((t) => t.priority !== "URGENT" && t.priority !== "HIGH") ||
    [];

  const getPriorityColor = (priority: string) => {
    switch (priority?.toUpperCase()) {
      case "URGENT":
        return "destructive";
      case "HIGH":
        return "default";
      case "MEDIUM":
        return "secondary";
      default:
        return "outline";
    }
  };

  const formatDueDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.ceil(
      (date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24),
    );

    if (diffDays < 0) return "Overdue";
    if (diffDays === 0) return "Due today";
    if (diffDays === 1) return "Due tomorrow";
    return `Due in ${diffDays} days`;
  };

  if (isLoading) {
    return (
      <Card className="lg:col-span-4">
        <CardHeader>
          <CardTitle>My Tasks</CardTitle>
          <CardDescription>Loading your tasks...</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-4">
              <Skeleton className="h-10 w-16" />
              <div className="flex-1 space-y-1">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-24" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="lg:col-span-4">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5" />
              My Tasks
            </CardTitle>
            <CardDescription>
              {totalPendingTasks} pending tasks
              {(jobTitle || department) && (
                <span className="ml-2">
                  · {jobTitle && <span>{jobTitle}</span>}
                  {jobTitle && department && ", "}
                  {department && <span>{department}</span>}
                </span>
              )}
            </CardDescription>
          </div>
          {urgentTaskCount > 0 && (
            <Badge variant="destructive" className="flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" />
              {urgentTaskCount} urgent
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Quick Patient Search */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Quick patient lookup..."
                className="pl-8"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Button variant="outline" size="icon" asChild>
              <Link to="/patients" search={{ q: searchQuery || undefined }}>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>

          {/* Task Queue */}
          {totalPendingTasks > 0 ? (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <CheckSquare className="h-4 w-4" />
                Task Queue
              </h4>
              <div className="space-y-2">
                {/* Show urgent tasks first, then high, then others */}
                {[...urgentTasks, ...highTasks, ...normalTasks]
                  .slice(0, 5)
                  .map((task) => (
                    <div
                      key={task.id}
                      className="flex items-start gap-3 py-2 px-3 rounded-md bg-muted/50 hover:bg-muted/80 transition-colors"
                    >
                      <Badge
                        variant={getPriorityColor(task.priority)}
                        className="text-[10px] px-1.5 py-0 mt-0.5"
                      >
                        {task.priority}
                      </Badge>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium line-clamp-1">
                          {task.title}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          {task.patient_name && (
                            <span className="text-xs text-muted-foreground truncate">
                              {task.patient_name}
                            </span>
                          )}
                          {task.due_date && (
                            <span className="text-xs text-muted-foreground flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {formatDueDate(task.due_date)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                {totalPendingTasks > 5 && (
                  <Button variant="ghost" size="sm" className="w-full" asChild>
                    <Link to="/tasks">
                      View all {totalPendingTasks} tasks
                      <ArrowRight className="h-4 w-4 ml-1" />
                    </Link>
                  </Button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-6 text-muted-foreground">
              <CheckSquare className="h-10 w-10 mb-2 opacity-50" />
              <p className="text-sm">No pending tasks</p>
              <p className="text-xs">You're all caught up!</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
