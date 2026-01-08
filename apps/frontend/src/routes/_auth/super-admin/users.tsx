import { createFileRoute } from "@tanstack/react-router";
import { RoleGuard } from "@/components/auth/RoleGuard";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { UserManagementTable } from "@/components/super-admin/UserManagementTable";

export const Route = createFileRoute("/_auth/super-admin/users")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <RoleGuard allowedRoles={["super_admin"]}>
      <Header fixed>
        <h1 className="text-lg font-semibold">Users</h1>
      </Header>
      <Main>
        <UserManagementTable />
      </Main>
    </RoleGuard>
  );
}
