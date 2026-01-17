import { auth } from "@/lib/firebase";
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/_auth")({
  beforeLoad: async ({ location }) => {
    // Basic check for auth.
    // Note: In a production app, you should wait for the auth state to be initialized
    // or use a context-based approach with TanStack Router.
    const user = auth.currentUser;
    if (!user) {
      throw redirect({
        to: "/login",
        search: {
          redirect: location.href,
        },
      });
    }
  },
  component: AuthLayout,
});

function AuthLayout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Outlet />
    </div>
  );
}
