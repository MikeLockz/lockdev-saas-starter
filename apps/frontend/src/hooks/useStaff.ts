import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useCurrentOrg } from "./useCurrentOrg";

// Types
export interface Staff {
  id: string;
  user_id: string;
  organization_id: string;
  job_title: string | null;
  department: string | null;
  employee_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user_email: string | null;
  user_display_name: string | null;
}

export interface StaffListItem {
  id: string;
  user_id: string;
  job_title: string | null;
  department: string | null;
  is_active: boolean;
  user_email: string | null;
  user_display_name: string | null;
}

export interface PaginatedStaff {
  items: StaffListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface StaffCreate {
  user_id: string;
  job_title?: string;
  department?: string;
  employee_id?: string;
}

export interface StaffUpdate {
  job_title?: string;
  department?: string;
  employee_id?: string;
  is_active?: boolean;
}

// Hooks
export function useStaff(options?: {
  department?: string;
  isActive?: boolean;
}) {
  const { orgId } = useCurrentOrg();

  return useQuery<PaginatedStaff>({
    queryKey: ["staff", orgId, options],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (options?.department) params.set("department", options.department);
      if (options?.isActive !== undefined)
        params.set("is_active", String(options.isActive));

      const response = await api.get(
        `/api/v1/organizations/${orgId}/staff?${params}`,
      );
      return response.data;
    },
    enabled: !!orgId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useStaffMember(staffId: string | undefined) {
  const { orgId } = useCurrentOrg();

  return useQuery<Staff>({
    queryKey: ["staffMember", orgId, staffId],
    queryFn: async () => {
      const response = await api.get(
        `/api/v1/organizations/${orgId}/staff/${staffId}`,
      );
      return response.data;
    },
    enabled: !!orgId && !!staffId,
  });
}

export function useCreateStaff() {
  const queryClient = useQueryClient();
  const { orgId } = useCurrentOrg();

  return useMutation({
    mutationFn: async (data: StaffCreate) => {
      const response = await api.post(
        `/api/v1/organizations/${orgId}/staff`,
        data,
      );
      return response.data as Staff;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff", orgId] });
    },
  });
}

export function useUpdateStaff() {
  const queryClient = useQueryClient();
  const { orgId } = useCurrentOrg();

  return useMutation({
    mutationFn: async ({
      staffId,
      data,
    }: {
      staffId: string;
      data: StaffUpdate;
    }) => {
      const response = await api.patch(
        `/api/v1/organizations/${orgId}/staff/${staffId}`,
        data,
      );
      return response.data as Staff;
    },
    onSuccess: (_, { staffId }) => {
      queryClient.invalidateQueries({ queryKey: ["staff", orgId] });
      queryClient.invalidateQueries({
        queryKey: ["staffMember", orgId, staffId],
      });
    },
  });
}

export function useDeleteStaff() {
  const queryClient = useQueryClient();
  const { orgId } = useCurrentOrg();

  return useMutation({
    mutationFn: async (staffId: string) => {
      await api.delete(`/api/v1/organizations/${orgId}/staff/${staffId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff", orgId] });
    },
  });
}

/**
 * Get the staff profile for the current user.
 * Returns null if the current user is not a staff member.
 */
export function useCurrentUserStaff() {
  const { orgId } = useCurrentOrg();
  const { data: staffList, isLoading } = useStaff();

  return useQuery<Staff | null>({
    queryKey: ["current-user-staff", orgId],
    queryFn: async () => {
      // Get current user ID
      const userResponse = await api.get("/api/v1/users/me");
      const userId = userResponse.data?.id;

      if (!userId || !staffList?.items) return null;

      // Find staff matching current user
      const match = staffList.items.find((s) => s.user_id === userId);
      if (!match) return null;

      // Fetch full staff details
      const response = await api.get(
        `/api/v1/organizations/${orgId}/staff/${match.id}`,
      );
      return response.data;
    },
    enabled: !!orgId && !isLoading && !!staffList?.items?.length,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
