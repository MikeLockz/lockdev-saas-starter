import { Navigate } from "@tanstack/react-router";
import { Skeleton } from "@/components/ui/skeleton";
import { type UserRole, useUserRole } from "@/hooks/useUserRole";

interface RoleGuardProps {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGuard({
  allowedRoles,
  children,
  fallback,
}: RoleGuardProps) {
  const { roleInfo, isLoading } = useUserRole();

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!roleInfo || !allowedRoles.includes(roleInfo.role)) {
    return fallback ? fallback : <Navigate to="/403" />;
  }

  return <>{children}</>;
}
