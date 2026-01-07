import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";

export interface ProxyProfile {
    id: string;
    user_id: string;
    relationship_to_patient: string | null;
    created_at: string;
}

/**
 * Hook to get the current user's proxy profile.
 * Returns null if the user is not a proxy.
 */
export function useCurrentUserProxy() {
    return useQuery<ProxyProfile | null>({
        queryKey: ["proxy", "me"],
        queryFn: async () => {
            try {
                const response = await api.get("/api/v1/users/me/proxy");
                return response.data;
            } catch (error: any) {
                // 404 means no proxy profile, return null
                if (error.response?.status === 404) {
                    return null;
                }
                throw error;
            }
        },
    });
}
