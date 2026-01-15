import { createFileRoute } from "@tanstack/react-router";
import { z } from "zod";
import { InviteAccept } from "../components/org/InviteAccept";

export const Route = createFileRoute("/invite/$token")({
  component: InvitePage,
  validateSearch: z.object({
    returnTo: z.string().optional(),
  }),
});

function InvitePage() {
  const { token } = Route.useParams();
  return <InviteAccept token={token} />;
}
