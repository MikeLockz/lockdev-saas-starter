import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/axios";
import { useOrgStore } from "@/store/org-store";

export type Task = {
  id: string;
  organization_id: string;
  patient_id?: string;
  assignee_id: string;
  created_by_id: string;
  title: string;
  description?: string;
  status: "TODO" | "IN_PROGRESS" | "DONE" | "CANCELLED";
  priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
  due_date?: string;
  completed_at?: string;
  created_at: string;
  assignee_name?: string;
  patient_name?: string;
};

export type CreateTaskData = {
  title: string;
  description?: string;
  priority: string;
  assignee_id: string;
  patient_id?: string;
  due_date?: string;
};

export type UpdateTaskData = {
  title?: string;
  description?: string;
  priority?: string;
  status?: string;
  assignee_id?: string;
  due_date?: string;
};

export const useTasks = (filters?: {
  status?: string;
  assignee_id?: string;
  priority?: string;
}) => {
  const currentOrgId = useOrgStore((state) => state.currentOrgId);
  return useQuery({
    queryKey: ["tasks", currentOrgId, filters],
    queryFn: async () => {
      if (!currentOrgId) return [];
      const params = new URLSearchParams();
      if (filters?.status) params.append("status", filters.status);
      if (filters?.assignee_id)
        params.append("assignee_id", filters.assignee_id);
      if (filters?.priority) params.append("priority", filters.priority);

      const response = await api.get<Task[]>(
        `/api/v1/organizations/${currentOrgId}/tasks?${params.toString()}`,
      );
      return response.data;
    },
    enabled: !!currentOrgId,
  });
};

export const useMyTasks = () => {
  return useQuery({
    queryKey: ["my-tasks"],
    queryFn: async () => {
      const response = await api.get<Task[]>("/api/v1/users/tasks/me/all");
      return response.data;
    },
  });
};

export const useCreateTask = () => {
  const currentOrgId = useOrgStore((state) => state.currentOrgId);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateTaskData) => {
      if (!currentOrgId) throw new Error("No organization selected");
      const response = await api.post<Task>(
        `/api/v1/organizations/${currentOrgId}/tasks`,
        data,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["my-tasks"] });
      toast.success("Task created successfully");
    },
    onError: () => {
      toast.error("Failed to create task");
    },
  });
};

export const useUpdateTask = () => {
  const currentOrgId = useOrgStore((state) => state.currentOrgId);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateTaskData }) => {
      if (!currentOrgId) throw new Error("No organization selected");
      const response = await api.patch<Task>(
        `/api/v1/organizations/${currentOrgId}/tasks/${id}`,
        data,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["my-tasks"] });
      toast.success("Task updated successfully");
    },
    onError: () => {
      toast.error("Failed to update task");
    },
  });
};

export const useDeleteTask = () => {
  const currentOrgId = useOrgStore((state) => state.currentOrgId);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      if (!currentOrgId) throw new Error("No organization selected");
      await api.delete(`/api/v1/organizations/${currentOrgId}/tasks/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["my-tasks"] });
      toast.success("Task deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete task");
    },
  });
};
