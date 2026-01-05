import { useMemo } from 'react';
import { useCurrentUser } from './api/useCurrentUser';
import { useCurrentUserProvider } from './useProviders';
import { useCurrentUserPatient } from './api/usePatients';
import { useCurrentUserStaff } from './useStaff';
import { useCurrentUserProxy } from './api/useProxy';

/**
 * User role types in priority order (highest to lowest)
 */
export type UserRole = 'super_admin' | 'admin' | 'provider' | 'staff' | 'proxy' | 'patient' | 'member';

export interface UserRoleInfo {
    /** Primary role for the user (highest priority role they have) */
    role: UserRole;
    /** Is a super admin (platform-level access) */
    isSuperAdmin: boolean;
    /** Is a provider in the current organization */
    isProvider: boolean;
    /** Is a staff member in the current organization */
    isStaff: boolean;
    /** Is a proxy for one or more patients */
    isProxy: boolean;
    /** Is a patient in the current organization */
    isPatient: boolean;
    /** Provider ID if user is a provider */
    providerId?: string;
    /** Patient ID if user is a patient */
    patientId?: string;
    /** Staff ID if user is a staff member */
    staffId?: string;
    /** Proxy ID if user is a proxy */
    proxyId?: string;
}

export interface UseUserRoleResult {
    roleInfo: UserRoleInfo | null;
    isLoading: boolean;
}

/**
 * Hook that provides the current user's role information.
 * 
 * Role priority (highest to lowest):
 * 1. super_admin - Platform-level admin
 * 2. provider - Healthcare provider
 * 3. staff - Organization staff member
 * 4. proxy - Patient guardian/caregiver
 * 5. patient - Patient
 * 6. member - Basic organization member
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { roleInfo, isLoading } = useUserRole();
 *   
 *   if (isLoading) return <Spinner />;
 *   
 *   if (roleInfo?.isProxy) {
 *     return <ProxyView proxyId={roleInfo.proxyId} />;
 *   }
 * }
 * ```
 */
export function useUserRole(): UseUserRoleResult {
    const { data: currentUser, isLoading: isUserLoading } = useCurrentUser();
    const { data: providerProfile, isLoading: isProviderLoading } = useCurrentUserProvider();
    const { data: patientProfile, isLoading: isPatientLoading } = useCurrentUserPatient();
    const { data: staffProfile, isLoading: isStaffLoading } = useCurrentUserStaff();
    const { data: proxyProfile, isLoading: isProxyLoading } = useCurrentUserProxy();

    const isLoading = isUserLoading || isProviderLoading || isPatientLoading || isStaffLoading || isProxyLoading;

    const roleInfo = useMemo<UserRoleInfo | null>(() => {
        if (!currentUser) return null;

        const isSuperAdmin = currentUser.is_super_admin ?? false;
        const isProvider = !!providerProfile;
        const isStaff = !!staffProfile;
        const isProxy = !!proxyProfile;
        const isPatient = !!patientProfile;

        // Determine primary role based on priority
        let role: UserRole = 'member';
        if (isSuperAdmin) {
            role = 'super_admin';
        } else if (isProvider) {
            role = 'provider';
        } else if (isStaff) {
            role = 'staff';
        } else if (isProxy) {
            role = 'proxy';
        } else if (isPatient) {
            role = 'patient';
        }

        return {
            role,
            isSuperAdmin,
            isProvider,
            isStaff,
            isProxy,
            isPatient,
            providerId: providerProfile?.id,
            patientId: patientProfile?.id,
            staffId: staffProfile?.id,
            proxyId: proxyProfile?.id,
        };
    }, [currentUser, providerProfile, patientProfile, staffProfile, proxyProfile]);

    return { roleInfo, isLoading };
}
