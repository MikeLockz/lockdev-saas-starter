import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/axios";
// Assuming Consent types might be in api-types, otherwise using any for now or defining locally
// import { ConsentRead } from "@/lib/api-types"; 

export interface ConsentRequirement {
    document_id: string;
    version_id: string;
    document_type: string;
    title: string;
}

export const useRequiredConsents = () => {
    return useQuery<ConsentRequirement[]>({
        queryKey: ["required-consents"],
        queryFn: async () => {
            const response = await api.get("/api/v1/consent/required");
            return response.data;
        },
    });
};
