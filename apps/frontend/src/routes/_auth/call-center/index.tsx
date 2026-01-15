import { createFileRoute } from "@tanstack/react-router";
import { z } from "zod";
import { CallCenterDashboard } from "@/components/calls/CallCenterDashboard";

export const Route = createFileRoute("/_auth/call-center/")({
  component: CallCenterDashboard,
  validateSearch: z.object({
    status: z.string().optional(),
  }),
});
