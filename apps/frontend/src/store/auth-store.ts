import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  role?: string; // Legacy single role
  roles?: string[]; // Array of roles
  mfa_enabled?: boolean;
  requires_consent?: boolean;
}

interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isImpersonating: boolean;
  setUser: (user: UserProfile | null) => void;
  setImpersonating: (isImpersonating: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isImpersonating: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setImpersonating: (isImpersonating) => set({ isImpersonating }),
      logout: () =>
        set({ user: null, isAuthenticated: false, isImpersonating: false }),
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => sessionStorage),
    },
  ),
);
