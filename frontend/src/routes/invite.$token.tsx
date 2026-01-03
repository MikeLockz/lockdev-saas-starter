
import { createFileRoute } from "@tanstack/react-router";
import { InviteAccept } from "../components/org/InviteAccept";
import { z } from "zod";

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
