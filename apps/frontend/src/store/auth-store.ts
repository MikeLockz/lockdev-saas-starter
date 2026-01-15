import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { User } from "@/lib/models";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isImpersonating: boolean;
  setUser: (user: User | null) => void;
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
