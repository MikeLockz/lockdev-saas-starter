import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

interface AuthState {
  userProfile: any | null;
  isAuthenticated: boolean;
  isImpersonating: boolean;
  setUserProfile: (profile: any | null) => void;
  setAuthenticated: (status: boolean) => void;
  setImpersonating: (status: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      userProfile: null,
      isAuthenticated: false,
      isImpersonating: false,
      setUserProfile: (profile) => set({ userProfile: profile }),
      setAuthenticated: (status) => set({ isAuthenticated: status }),
      setImpersonating: (status) => set({ isImpersonating: status }),
      logout: () => set({ userProfile: null, isAuthenticated: false, isImpersonating: false }),
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => sessionStorage),
    },
  ),
);
