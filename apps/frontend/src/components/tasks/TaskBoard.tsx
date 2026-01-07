import { isPast, isToday } from "date-fns";
import {
  Calendar,
  Kanban as KanbanIcon,
  List,
  Plus,
  Trash2,
  User,
} from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useTimezoneContext } from "@/contexts/TimezoneContext";
import { type PatientListItem, usePatients } from "@/hooks/api/usePatients";
import { type StaffMember, useStaff } from "@/hooks/api/useStaff";
import {
  type Task,
  useCreateTask,
  useDeleteTask,
  useTasks,
  useUpdateTask,
} from "@/hooks/api/useTasks";
import { formatDateTime } from "@/lib/timezone";
import { cn } from "@/lib/utils";

export function TaskCreateModal({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const createTask = useCreateTask();
  const { data: patientsData } = usePatients();
  const patients = patientsData?.items || [];
  const { data: staff } = useStaff();

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm();

  const onSubmit = (data: any) => {
    createTask.mutate(data, {
      onSuccess: () => {
        reset();
        onOpenChange(false);
      },
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Task</DialogTitle>
          <DialogDescription>Assign a task to a team member.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label>Title</Label>
            <Input
              {...register("title", { required: true })}
              placeholder="Task title"
            />
            {errors.title && (
              <span className="text-red-500 text-sm">Required</span>
            )}
          </div>

          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea {...register("description")} placeholder="Details..." />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Priority</Label>
              <Select
                onValueChange={(val) => setValue("priority", val)}
                defaultValue="MEDIUM"
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="LOW">Low</SelectItem>
                  <SelectItem value="MEDIUM">Medium</SelectItem>
                  <SelectItem value="HIGH">High</SelectItem>
                  <SelectItem value="URGENT">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Due Date</Label>
              <Input type="date" {...register("due_date")} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Assignee</Label>
              <Select onValueChange={(val) => setValue("assignee_id", val)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select staff" />
                </SelectTrigger>
                <SelectContent>
                  {staff?.map((s: StaffMember) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Patient (Optional)</Label>
              <Select
                onValueChange={(val) =>
                  setValue("patient_id", val === "none" ? undefined : val)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select patient" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {patients.map((p: PatientListItem) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.first_name} {p.last_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <Button type="submit">Create Task</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function TaskCard({ task }: { task: Task }) {
  const timezone = useTimezoneContext();
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();

  const priorityColor =
    {
      LOW: "bg-slate-100 text-slate-700",
      MEDIUM: "bg-blue-100 text-blue-700",
      HIGH: "bg-orange-100 text-orange-700",
      URGENT: "bg-red-100 text-red-700",
    }[task.priority] || "bg-slate-100";

  const isOverdue =
    task.due_date &&
    isPast(new Date(task.due_date)) &&
    !isToday(new Date(task.due_date)) &&
    task.status !== "DONE";

  return (
    <div className="bg-card border rounded-lg p-3 shadow-sm space-y-3 hover:shadow-md transition-shadow group relative">
      <div className="flex justify-between items-start">
        <Badge
          variant="secondary"
          className={cn("text-[10px] px-1 py-0", priorityColor)}
        >
          {task.priority}
        </Badge>
        <button
          onClick={() => deleteTask.mutate(task.id)}
          className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-red-500 transition-opacity"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      <div>
        <h4 className="font-medium text-sm leading-tight">{task.title}</h4>
        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
          {task.description}
        </p>
      </div>

      <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t mt-2">
        <div className="flex items-center space-x-2">
          <Avatar className="h-5 w-5">
            <AvatarFallback className="text-[9px]">
              <User className="h-3 w-3" />
            </AvatarFallback>
          </Avatar>
          <span>{task.assignee_name || "Unassigned"}</span>
        </div>
        {task.due_date && (
          <div
            className={cn(
              "flex items-center",
              isOverdue && "text-red-500 font-medium",
            )}
          >
            <Calendar className="h-3 w-3 mr-1" />
            {formatDateTime(new Date(task.due_date), "MMM d", timezone)}
          </div>
        )}
      </div>

      <div className="flex space-x-1 pt-1">
        {task.status !== "TODO" && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-[10px] flex-1 bg-muted/50"
            onClick={() =>
              updateTask.mutate({ id: task.id, data: { status: "TODO" } })
            }
          >
            To Todo
          </Button>
        )}
        {task.status !== "IN_PROGRESS" && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-[10px] flex-1 bg-blue-50 text-blue-600 hover:bg-blue-100 hover:text-blue-700"
            onClick={() =>
              updateTask.mutate({
                id: task.id,
                data: { status: "IN_PROGRESS" },
              })
            }
          >
            Start
          </Button>
        )}
        {task.status !== "DONE" && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-[10px] flex-1 bg-green-50 text-green-600 hover:bg-green-100 hover:text-green-700"
            onClick={() =>
              updateTask.mutate({ id: task.id, data: { status: "DONE" } })
            }
          >
            Done
          </Button>
        )}
      </div>
    </div>
  );
}

export function TaskBoard() {
  const { data: tasks } = useTasks();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [view, setView] = useState<"board" | "list">("board");

  const todoTasks = tasks?.filter((t: Task) => t.status === "TODO") || [];
  const inProgressTasks =
    tasks?.filter((t: Task) => t.status === "IN_PROGRESS") || [];
  const doneTasks = tasks?.filter((t: Task) => t.status === "DONE") || [];

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Task Board</h2>
          <p className="text-muted-foreground">
            Manage ongoing tasks and assignments
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="bg-muted p-1 rounded-md flex space-x-1 mr-4">
            <Button
              variant={view === "board" ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setView("board")}
              className="h-8 w-8 p-0"
            >
              <KanbanIcon className="h-4 w-4" />
            </Button>
            <Button
              variant={view === "list" ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setView("list")}
              className="h-8 w-8 p-0"
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" /> New Task
          </Button>
        </div>
      </div>

      <TaskCreateModal open={isCreateOpen} onOpenChange={setIsCreateOpen} />

      {view === "board" ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-1 h-[calc(100vh-200px)] overflow-hidden">
          {/* TODO Column */}
          <div className="flex flex-col h-full bg-slate-50/50 rounded-lg p-4 border border-dashed hover:border-solid transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-sm uppercase text-slate-500">
                To Do
              </h3>
              <Badge variant="secondary">{todoTasks.length}</Badge>
            </div>
            <div className="space-y-3 overflow-y-auto flex-1 pr-1">
              {todoTasks.map((task: Task) => (
                <TaskCard key={task.id} task={task} />
              ))}
            </div>
          </div>

          {/* IN PROGRESS Column */}
          <div className="flex flex-col h-full bg-blue-50/30 rounded-lg p-4 border border-dashed border-blue-200 hover:border-solid transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-sm uppercase text-blue-500">
                In Progress
              </h3>
              <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-200">
                {inProgressTasks.length}
              </Badge>
            </div>
            <div className="space-y-3 overflow-y-auto flex-1 pr-1">
              {inProgressTasks.map((task: Task) => (
                <TaskCard key={task.id} task={task} />
              ))}
            </div>
          </div>

          {/* DONE Column */}
          <div className="flex flex-col h-full bg-green-50/30 rounded-lg p-4 border border-dashed border-green-200 hover:border-solid transition-colors">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-sm uppercase text-green-500">
                Done
              </h3>
              <Badge className="bg-green-100 text-green-700 hover:bg-green-200">
                {doneTasks.length}
              </Badge>
            </div>
            <div className="space-y-3 overflow-y-auto flex-1 pr-1">
              {doneTasks.map((task: Task) => (
                <TaskCard key={task.id} task={task} />
              ))}
            </div>
          </div>
        </div>
      ) : (
        <Card>
          <CardContent>
            <div className="py-8 text-center text-muted-foreground">
              List view not implemented yet.
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
