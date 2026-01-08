import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { Organization } from "@/lib/models";

interface OrgState {
  currentOrgId: Organization["id"] | null;
  setCurrentOrgId: (id: Organization["id"] | null) => void;
}

export const useOrgStore = create<OrgState>()(
  persist(
    (set) => ({
      currentOrgId: null,
      setCurrentOrgId: (id) => set({ currentOrgId: id }),
    }),
    {
      name: "org-storage",
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
