import { createRootRoute, Outlet } from "@tanstack/react-router";
import { NotFound } from "@/components/layout/NotFound";
import { Toaster } from "@/components/ui/sonner";

export const Route = createRootRoute({
  component: () => (
    <>
      <Outlet />
      <Toaster />
    </>
  ),
  notFoundComponent: NotFound,
});
