import { create } from "zustand";
import { persist } from "zustand/middleware";

interface Organization {
  id: string;
  name: string;
  slug: string;
}

interface OrgState {
  organizations: Organization[];
  currentOrg: Organization | null;
  setOrganizations: (orgs: Organization[]) => void;
  setCurrentOrg: (org: Organization | null) => void;
}

export const useOrgStore = create<OrgState>()(
  persist(
    (set) => ({
      organizations: [],
      currentOrg: null,
      setOrganizations: (orgs) => set({ organizations: orgs }),
      setCurrentOrg: (org) => set({ currentOrg: org }),
    }),
    {
      name: "org-storage",
    },
  ),
);
