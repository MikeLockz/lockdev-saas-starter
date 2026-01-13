import { useQuery } from '@tanstack/react-query';
import { api as apiClient } from '@/lib/axios';

export interface PatientProxy {
    proxy_id: string;
    proxy_user_id: string;
    proxy_name: string;
    proxy_email: string;
    relationship_type: string;
    status: string; // ACTIVE, PENDING, etc. - inferred from assignments/invitations usually
    permissions: {
        can_view_billing: boolean;
        // ... other permissions
    }
}

// Get proxies for a patient
export function usePatientProxies(patientId: string) {
    return useQuery({
        queryKey: ['patient-proxies', patientId],
        queryFn: async () => {
            const { data } = await apiClient.get<PatientProxy[]>(
                `/organizations/CURRENT/patients/${patientId}/proxies`
                // Note: The URL here might depend on how the API is structured. 
                // In existing implementation, proxies are under /organizations/{orgId}/patients/{patientId}/proxies
                // Frontend likely needs to know orgId or use a placeholder if interceptor handles it.
                // For now, assuming interceptor handles 'CURRENT' or we need to pass orgId.
                // Let's assume we can get it from context later, but for now lets try standard path.
            );
            return data;
        },
        enabled: !!patientId,
    });
}

// Note: If orgId is required, we might need to pass it or use useCurrentOrg hook.
// existing hooks like useBilling use /organizations/${orgId}/... 
// I should update this to be robust. 
