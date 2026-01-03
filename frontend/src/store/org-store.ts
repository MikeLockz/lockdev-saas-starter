import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface OrgState {
    currentOrgId: string | null;
    setCurrentOrgId: (id: string | null) => void;
}

export const useOrgStore = create<OrgState>()(
    persist(
        (set) => ({
            currentOrgId: null,
            setCurrentOrgId: (id) => set({ currentOrgId: id }),
        }),
        {
            name: 'org-storage',
            storage: createJSONStorage(() => localStorage),
        }
    )
);
