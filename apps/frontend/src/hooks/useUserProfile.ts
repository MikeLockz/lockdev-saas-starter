import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useAuth } from "./useAuth";

// Types
export interface UserProfile {
  id: string;
  email: string;
  display_name?: string;
  full_name?: string;
  is_active: boolean;
  is_super_admin: boolean;
  mfa_enabled?: boolean;
  transactional_consent?: boolean;
  marketing_consent?: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdate {
  display_name?: string;
  full_name?: string;
}

export function useUserProfile() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const {
    data: profile,
    isLoading,
    error,
  } = useQuery<UserProfile>({
    queryKey: ["userProfile"],
    queryFn: async () => {
      const token = await user?.getIdToken();
      const response = await api.get("/api/v1/users/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
    enabled: !!user,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const updateProfile = useMutation({
    mutationFn: async (data: UserProfileUpdate) => {
      const token = await user?.getIdToken();
      const response = await api.patch("/api/v1/users/me", data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["userProfile"] });
    },
  });

  return {
    profile,
    isLoading,
    error,
    updateProfile,
  };
}
