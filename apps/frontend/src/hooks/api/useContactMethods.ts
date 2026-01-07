import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useOrgStore } from "@/store/org-store";
import type { ContactMethod } from "./usePatients";

export interface ContactMethodCreate {
    type: string;
    value: string;
    is_primary?: boolean;
    is_safe_for_voicemail?: boolean;
    label?: string;
}

export interface ContactMethodUpdate extends Partial<ContactMethodCreate> { }

// Hooks
export const useContactMethods = (patientId: string) => {
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useQuery<ContactMethod[]>({
        queryKey: ["contactMethods", currentOrgId, patientId],
        queryFn: async () => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.get(
                `/api/v1/organizations/${currentOrgId}/patients/${patientId}/contact-methods`
            );
            return response.data;
        },
        enabled: !!currentOrgId && !!patientId,
    });
};

export const useCreateContactMethod = (patientId: string) => {
    const queryClient = useQueryClient();
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation({
        mutationFn: async (data: ContactMethodCreate) => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.post(
                `/api/v1/organizations/${currentOrgId}/patients/${patientId}/contact-methods`,
                data
            );
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["contactMethods", currentOrgId, patientId] });
            queryClient.invalidateQueries({ queryKey: ["patient", currentOrgId, patientId] });
        },
    });
};

export const useUpdateContactMethod = (patientId: string) => {
    const queryClient = useQueryClient();
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation({
        mutationFn: async ({ contactId, data }: { contactId: string; data: ContactMethodUpdate }) => {
            if (!currentOrgId) throw new Error("No organization selected");
            const response = await api.patch(
                `/api/v1/organizations/${currentOrgId}/patients/${patientId}/contact-methods/${contactId}`,
                data
            );
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["contactMethods", currentOrgId, patientId] });
            queryClient.invalidateQueries({ queryKey: ["patient", currentOrgId, patientId] });
        },
    });
};

export const useDeleteContactMethod = (patientId: string) => {
    const queryClient = useQueryClient();
    const currentOrgId = useOrgStore((state) => state.currentOrgId);

    return useMutation({
        mutationFn: async (contactId: string) => {
            if (!currentOrgId) throw new Error("No organization selected");
            await api.delete(
                `/api/v1/organizations/${currentOrgId}/patients/${patientId}/contact-methods/${contactId}`
            );
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["contactMethods", currentOrgId, patientId] });
            queryClient.invalidateQueries({ queryKey: ["patient", currentOrgId, patientId] });
        },
    });
};
