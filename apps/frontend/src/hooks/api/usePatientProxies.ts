import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useOrgStore } from "@/store/org-store";

// Types
export interface ProxyPermissions {
  can_view_profile: boolean;
  can_view_appointments: boolean;
  can_schedule_appointments: boolean;
  can_view_clinical_notes: boolean;
  can_view_billing: boolean;
  can_message_providers: boolean;
}

export interface ProxyUserInfo {
  id: string;
  email: string;
  display_name: string | null;
}

export interface ProxyAssignment {
  id: string;
  proxy_id: string;
  patient_id: string;
  relationship_type: string;
  can_view_profile: boolean;
  can_view_appointments: boolean;
  can_schedule_appointments: boolean;
  can_view_clinical_notes: boolean;
  can_view_billing: boolean;
  can_message_providers: boolean;
  granted_at: string;
  expires_at: string | null;
  revoked_at: string | null;
  user: ProxyUserInfo;
}

export interface ProxyListResponse {
  patient_id: string;
  proxies: ProxyAssignment[];
}

export interface ProxyAssignmentCreate {
  email: string;
  relationship_type: string;
  permissions?: Partial<ProxyPermissions>;
  expires_at?: string;
}

export interface ProxyAssignmentUpdate {
  permissions?: Partial<ProxyPermissions>;
  expires_at?: string | null;
}

// Hooks
export const usePatientProxies = (patientId: string) => {
  const currentOrgId = useOrgStore((state) => state.currentOrgId);

  return useQuery<ProxyListResponse>({
    queryKey: ["patient-proxies", currentOrgId, patientId],
    queryFn: async () => {
      if (!currentOrgId) throw new Error("No organization selected");
      const response = await api.get(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/proxies`,
      );
      return response.data;
    },
    enabled: !!currentOrgId && !!patientId,
  });
};

export const useAssignProxy = (patientId: string) => {
  const queryClient = useQueryClient();
  const currentOrgId = useOrgStore((state) => state.currentOrgId);

  return useMutation({
    mutationFn: async (data: ProxyAssignmentCreate) => {
      if (!currentOrgId) throw new Error("No organization selected");
      const response = await api.post(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/proxies`,
        data,
      );
      return response.data as ProxyAssignment;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["patient-proxies", currentOrgId, patientId],
      });
    },
  });
};

export const useUpdateProxyPermissions = (patientId: string) => {
  const queryClient = useQueryClient();
  const currentOrgId = useOrgStore((state) => state.currentOrgId);

  return useMutation({
    mutationFn: async ({
      assignmentId,
      data,
    }: {
      assignmentId: string;
      data: ProxyAssignmentUpdate;
    }) => {
      if (!currentOrgId) throw new Error("No organization selected");
      const response = await api.patch(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/proxies/${assignmentId}`,
        data,
      );
      return response.data as ProxyAssignment;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["patient-proxies", currentOrgId, patientId],
      });
    },
  });
};

export const useRevokeProxy = (patientId: string) => {
  const queryClient = useQueryClient();
  const currentOrgId = useOrgStore((state) => state.currentOrgId);

  return useMutation({
    mutationFn: async (assignmentId: string) => {
      if (!currentOrgId) throw new Error("No organization selected");
      await api.delete(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/proxies/${assignmentId}`,
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["patient-proxies", currentOrgId, patientId],
      });
    },
  });
};
