import { useQuery } from "@tanstack/react-query";
import { api as apiClient } from "@/lib/axios";

export interface PatientProfile {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  // Add other fields as needed
}

export function useCurrentPatient() {
  const { data: currentPatient, isLoading } = useQuery({
    queryKey: ["current-patient"],
    queryFn: async () => {
      // Assuming there is an endpoint to get the current user's patient profile
      // If the user can have multiple patient profiles, logic might need adjustment
      // For now, assuming 1:1 or getting the primary patient profile
      const { data } = await apiClient.get<PatientProfile>("/users/me/patient");
      return data;
    },
    retry: false,
  });

  return {
    currentPatient,
    isLoading,
  };
}
