import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { SupportTicketForm } from "../../../components/support/SupportTicketForm";

export const Route = createFileRoute("/_auth/help/contact")({
  component: ContactPage,
});

function ContactPage() {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto py-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">Contact Support</h1>
      <SupportTicketForm onSuccess={() => navigate({ to: "/help/tickets" })} />
    </div>
  );
}
