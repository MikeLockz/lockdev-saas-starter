import { createFileRoute, Link } from "@tanstack/react-router";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { TenantList } from "../../../components/super-admin/TenantList";
import { Button } from "../../../components/ui/button";

export const Route = createFileRoute("/_auth/super-admin/organizations")({
  component: OrganizationsPage,
});

function OrganizationsPage() {
  return (
    <>
      <Header fixed>
        <div className="flex items-center justify-between w-full">
          <h1 className="text-lg font-semibold">Organizations</h1>
          <Link to="/super-admin">
            <Button variant="outline" size="sm">
              ← Back to Dashboard
            </Button>
          </Link>
        </div>
      </Header>
      <Main>
        <TenantList />
      </Main>
    </>
  );
}
