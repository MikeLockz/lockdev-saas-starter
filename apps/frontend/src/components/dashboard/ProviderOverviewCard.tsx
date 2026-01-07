import {
  AlertTriangle,
  Calendar,
  CheckSquare,
  Clock,
  User,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useProviderPendingTasks,
  useProviderTodaysAppointments,
} from "@/hooks/api/useDashboardStats";

interface ProviderOverviewCardProps {
  providerId: string | undefined;
  userId: string | undefined;
}

/**
 * Provider Overview Card displays:
 * - Today's appointments timeline
 * - Pending tasks summary
 */
export function ProviderOverviewCard({
  providerId,
  userId,
}: ProviderOverviewCardProps) {
  const { data: appointments, isLoading: isApptLoading } =
    useProviderTodaysAppointments(providerId);
  const { data: tasks, isLoading: isTasksLoading } =
    useProviderPendingTasks(userId);

  const isLoading = isApptLoading || isTasksLoading;

  // Count urgent/high priority tasks
  const urgentTaskCount =
    tasks?.filter((t) => t.priority === "URGENT" || t.priority === "HIGH")
      .length || 0;
  const totalPendingTasks = tasks?.length || 0;

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  const getTypeColor = (type: string) => {
    switch (type?.toUpperCase()) {
      case "URGENT":
        return "destructive";
      case "INITIAL":
        return "default";
      case "FOLLOW_UP":
        return "secondary";
      default:
        return "outline";
    }
  };

  if (isLoading) {
    return (
      <Card className="lg:col-span-4">
        <CardHeader>
          <CardTitle>Today's Schedule</CardTitle>
          <CardDescription>
            Loading your appointments and tasks...
          </CardDescription>
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
              <Calendar className="h-5 w-5" />
              Today's Schedule
            </CardTitle>
            <CardDescription>
              {appointments?.length || 0} appointments · {totalPendingTasks}{" "}
              pending tasks
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
          {/* Appointments Timeline */}
          {appointments && appointments.length > 0 ? (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Appointments
              </h4>
              <div className="space-y-2 pl-4 border-l-2 border-muted">
                {appointments.slice(0, 5).map((appt) => (
                  <div
                    key={appt.id}
                    className="flex items-center gap-3 py-2 px-3 rounded-md bg-muted/50 hover:bg-muted/80 transition-colors"
                  >
                    <div className="text-sm font-medium text-primary min-w-[65px]">
                      {formatTime(appt.scheduled_at)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <User className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                        <span className="text-sm font-medium truncate">
                          {appt.patient_name || "Patient"}
                        </span>
                      </div>
                      {appt.reason && (
                        <p className="text-xs text-muted-foreground truncate mt-0.5">
                          {appt.reason}
                        </p>
                      )}
                    </div>
                    <Badge
                      variant={getTypeColor(appt.appointment_type)}
                      className="text-xs flex-shrink-0"
                    >
                      {appt.appointment_type?.toLowerCase().replace("_", " ") ||
                        "Visit"}
                    </Badge>
                  </div>
                ))}
                {appointments.length > 5 && (
                  <p className="text-xs text-muted-foreground pl-3">
                    +{appointments.length - 5} more appointments
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-6 text-muted-foreground">
              <Calendar className="h-10 w-10 mb-2 opacity-50" />
              <p className="text-sm">No appointments scheduled for today</p>
            </div>
          )}

          {/* Pending Tasks Summary */}
          {totalPendingTasks > 0 && (
            <div className="pt-3 border-t">
              <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2 mb-2">
                <CheckSquare className="h-4 w-4" />
                Pending Tasks ({totalPendingTasks})
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {tasks?.slice(0, 4).map((task) => (
                  <div
                    key={task.id}
                    className="p-2 rounded-md bg-muted/30 border border-muted"
                  >
                    <div className="flex items-start gap-2">
                      <Badge
                        variant={
                          task.priority === "URGENT" || task.priority === "HIGH"
                            ? "destructive"
                            : "secondary"
                        }
                        className="text-[10px] px-1.5 py-0"
                      >
                        {task.priority}
                      </Badge>
                    </div>
                    <p className="text-xs font-medium mt-1 line-clamp-2">
                      {task.title}
                    </p>
                  </div>
                ))}
              </div>
              {totalPendingTasks > 4 && (
                <p className="text-xs text-muted-foreground mt-2">
                  +{totalPendingTasks - 4} more tasks
                </p>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
