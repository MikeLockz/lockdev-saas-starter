import { createFileRoute, Link } from "@tanstack/react-router";
import { AlertCircle } from "lucide-react";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/403")({
  component: AccessDeniedPage,
});

function AccessDeniedPage() {
  return (
    <>
      <Header />
      <Main>
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6 text-center animate-in fade-in-50">
          <div className="flex bg-destructive/10 p-4 rounded-full">
            <AlertCircle className="h-10 w-10 text-destructive" />
          </div>
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight">Access Denied</h1>
            <p className="text-muted-foreground max-w-[400px]">
              You don't have permission to view this page. If you believe this
              is an error, please contact your administrator.
            </p>
          </div>
          <Button asChild size="lg">
            <Link to="/dashboard">Return to Dashboard</Link>
          </Button>
        </div>
      </Main>
    </>
  );
}
