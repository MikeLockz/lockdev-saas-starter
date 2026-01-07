import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";

// Types
export interface ProxyPatientInfo {
    id: string;
    first_name: string;
    last_name: string;
    dob: string;
    medical_record_number: string | null;
}

export interface ProxyPermissions {
    can_view_profile: boolean;
    can_view_appointments: boolean;
    can_schedule_appointments: boolean;
    can_view_clinical_notes: boolean;
    can_view_billing: boolean;
    can_message_providers: boolean;
}

export interface ProxyPatient {
    patient: ProxyPatientInfo;
    relationship_type: string;
    permissions: ProxyPermissions;
    granted_at: string;
    expires_at: string | null;
}

// Hook
export const useMyProxyPatients = () => {
    return useQuery<ProxyPatient[]>({
        queryKey: ["my-proxy-patients"],
        queryFn: async () => {
            const response = await api.get("/api/v1/users/me/proxy-patients");
            return response.data;
        },
    });
};
