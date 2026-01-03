import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useOrgStore } from "@/store/org-store";

// Types (since we don't have generated types for patients yet)
export interface ContactMethod {
    id: string;
    type: string;
    value: string;
    is_primary: boolean;
    is_safe_for_voicemail: boolean;
    label: string | null;
    created_at: string;
    updated_at: string;
}

export interface Patient {
    id: string;
    user_id: string | null;
    first_name: string;
    last_name: string;
    dob: string;
    legal_sex: string | null;
    medical_record_number: string | null;
    stripe_customer_id: string | null;
    subscription_status: string;
    contact_methods: ContactMethod[];
    enrolled_at: string | null;
    created_at: string;
    updated_at: string;
}

export interface PatientListItem {
    id: string;
    first_name: string;
    last_name: string;
    dob: string;
    medical_record_number: string | null;
    enrolled_at: string | null;
    status: string;
}

export interface PaginatedPatients {
    items: PatientListItem[];
    total: number;
    limit: number;
    offset: number;
}

export interface PatientSearchParams {
    name?: string;
    mrn?: string;
    status?: string;
    limit?: number;
    offset?: number;
}

export interface PatientCreate {
    first_name: string;
    last_name: string;
    dob: string;
    legal_sex?: string;
    medical_record_number?: string;
    contact_methods?: Omit<ContactMethod, 'id' | 'created_at' | 'updated_at'>[];
}

export interface PatientUpdate {
    first_name?: string;
    last_name?: string;
    dob?: string;
    legal_sex?: string;
    medical_record_number?: string;
}

// Hooks
export const usePatients = (params: PatientSearchParams = {}) => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<PaginatedPatients>({
        queryKey: ["patients", currentOrgId, params],
        queryFn: async () => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.get(`/api/v1/organizations/${currentOrgId}/patients`, {
                params: {
                    name: params.name,
                    mrn: params.mrn,
                    status: params.status,
                    limit: params.limit || 50,
                    offset: params.offset || 0,
                }
            });
            return response.data;
        },
        enabled: !!currentOrgId,
    });
};

export const usePatient = (patientId: string) => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<Patient>({
        queryKey: ["patient", currentOrgId, patientId],
        queryFn: async () => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.get(`/api/v1/organizations/${currentOrgId}/patients/${patientId}`);
            return response.data;
        },
        enabled: !!currentOrgId && !!patientId,
    });
};

export const useCreatePatient = () => {
    const queryClient = useQueryClient();
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation({
        mutationFn: async (data: PatientCreate) => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.post(`/api/v1/organizations/${currentOrgId}/patients`, data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["patients", currentOrgId] });
        },
    });
};

export const useUpdatePatient = (patientId: string) => {
    const queryClient = useQueryClient();
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation({
        mutationFn: async (data: PatientUpdate) => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.patch(`/api/v1/organizations/${currentOrgId}/patients/${patientId}`, data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["patient", currentOrgId, patientId] });
            queryClient.invalidateQueries({ queryKey: ["patients", currentOrgId] });
        },
    });
};

export const useDischargePatient = () => {
    const queryClient = useQueryClient();
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation({
        mutationFn: async (patientId: string) => {
            if (!currentOrgId) throw new Error("No organization selected");
            await api.delete(`/api/v1/organizations/${currentOrgId}/patients/${patientId}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["patients", currentOrgId] });
        },
    });
};
