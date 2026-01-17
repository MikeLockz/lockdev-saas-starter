import { useAuth } from "@/hooks/useAuth";
import { useAuthStore } from "@/store/auth-store";
import { Navigate, useLocation } from "@tanstack/react-router";
import type React from "react";

interface AuthGuardProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  requireMfa?: boolean;
}

export const AuthGuard = ({ children, allowedRoles, requireMfa }: AuthGuardProps) => {
  const { isAuthenticated, userProfile } = useAuthStore();
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user || !isAuthenticated) {
    return <Navigate to="/login" search={{ redirect: location.href }} />;
  }

  // Role check (simplified for now as userProfile.role might be a string)
  if (allowedRoles && !allowedRoles.includes(userProfile?.role)) {
    return <Navigate to="/" />;
  }

  // MFA check
  if (requireMfa && !userProfile?.mfa_enabled) {
    return <Navigate to="/setup-mfa" />;
  }

  return <>{children}</>;
};
