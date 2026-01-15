import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex-1 p-8 flex flex-col gap-4 items-center justify-center">
        <h3 className="text-2xl font-bold">Welcome to Lockdev SaaS</h3>
        <div className="flex gap-4">
          <Link to="/login">
            <Button>Login</Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="outline">Go to Dashboard</Button>
          </Link>
        </div>
      </div>
      <footer className="py-6 border-t">
        <div className="flex gap-4 justify-center text-sm text-muted-foreground">
          <Link to="/legal/privacy" className="hover:underline">
            Privacy Policy
          </Link>
          <Link to="/legal/terms" className="hover:underline">
            Terms of Service
          </Link>
        </div>
      </footer>
    </div>
  );
}
