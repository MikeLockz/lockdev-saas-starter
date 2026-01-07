import { useOrgStore } from '@/store/org-store';
import { useOrganizations } from './useOrganizations';
import { useUserProfile } from './useUserProfile';
import { useMemo, useEffect } from 'react';

export function useCurrentOrg() {
    const { currentOrgId, setCurrentOrgId } = useOrgStore();
    const { profile } = useUserProfile();
    const isSuperAdmin = profile?.is_super_admin ?? false;
    const { data: organizations, isLoading, error } = useOrganizations({ forSuperAdmin: isSuperAdmin });

    const currentOrg = useMemo(() =>
        organizations?.find(org => org.id === currentOrgId),
        [organizations, currentOrgId]
    );

    // Auto-select first org if none selected and orgs exist
    useEffect(() => {
        if (!isLoading && organizations && organizations.length > 0) {
            // If we have no selection, or the selection is invalid (not in list), select first
            const isValidSelection = currentOrgId && organizations.some(o => o.id === currentOrgId);
            if (!isValidSelection) {
                setCurrentOrgId(organizations[0].id);
            }
        }
    }, [currentOrgId, organizations, setCurrentOrgId, isLoading]);

    return {
        organization: currentOrg,
        isLoading,
        error,
        orgId: currentOrgId,
        organizations, // convenience export
        setCurrentOrgId
    };
}

