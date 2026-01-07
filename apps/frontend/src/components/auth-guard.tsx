import { useAuth } from "@/hooks/useAuth";
import { useAuthStore } from "@/store/auth-store";
import { Navigate } from "@tanstack/react-router";

interface AuthGuardProps {
    children: React.ReactNode;
    allowedRoles?: string[];
    requireMfa?: boolean;
}

export function AuthGuard({ children, allowedRoles, requireMfa }: AuthGuardProps) {
    const { user: firebaseUser, loading } = useAuth();
    const { user: profile } = useAuthStore();

    if (loading) {
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }

    if (!firebaseUser) {
        return <Navigate to="/login" />;
    }

    if (profile?.requires_consent) {
        return <Navigate to="/consent" />;
    }

    if (requireMfa && profile && !profile.mfa_enabled) {
         return <Navigate to="/settings" />; // Placeholder for MFA setup
    }

    if (allowedRoles && profile && profile.roles) {
        const hasRole = profile.roles.some(role => allowedRoles.includes(role));
        if (!hasRole) {
            return <div className="p-4 text-red-500">Access Denied: Insufficient Permissions</div>;
        }
    }

    return <>{children}</>;
}