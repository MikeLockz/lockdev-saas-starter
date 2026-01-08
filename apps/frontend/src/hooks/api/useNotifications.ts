import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";

// Types
export interface Notification {
  id: string;
  user_id: string;
  type: "APPOINTMENT" | "MESSAGE" | "SYSTEM" | "BILLING";
  title: string;
  body?: string;
  data_json?: Record<string, unknown>;
  is_read: boolean;
  read_at?: string;
  created_at: string;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  size: number;
}

export interface UnreadCountResponse {
  count: number;
}

// Hooks

export const useNotifications = (page = 1, size = 20, isRead?: boolean) => {
  return useQuery({
    queryKey: ["notifications", page, size, isRead],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        size: size.toString(),
      });
      if (isRead !== undefined) {
        params.append("is_read", isRead.toString());
      }
      const { data } = await api.get<NotificationListResponse>(
        `/api/v1/users/me/notifications?${params.toString()}`,
      );
      return data;
    },
  });
};

export const useUnreadCount = () => {
  return useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: async () => {
      const { data } = await api.get<UnreadCountResponse>(
        "/api/v1/users/me/notifications/unread-count",
      );
      return data;
    },
    refetchInterval: 30000, // Poll every 30s
  });
};

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (notificationId: string) => {
      const { data } = await api.patch<Notification>(
        `/api/v1/users/me/notifications/${notificationId}/read`,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};

export const useMarkAllNotificationsRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await api.post("/api/v1/users/me/notifications/read-all");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};

export const useDeleteNotification = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (notificationId: string) => {
      await api.delete(`/api/v1/users/me/notifications/${notificationId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
};
