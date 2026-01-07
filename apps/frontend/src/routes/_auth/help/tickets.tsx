import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { TicketDetail } from "../../../components/support/TicketDetail";
import { TicketList } from "../../../components/support/TicketList";
import { Button } from "../../../components/ui/button";
import type { SupportTicket } from "../../../hooks/api/useSupportTickets";

export const Route = createFileRoute("/_auth/help/tickets")({
  component: TicketsPage,
});

function TicketsPage() {
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(
    null,
  );

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">
          {selectedTicket ? "Ticket Detail" : "My Support Tickets"}
        </h1>
        {selectedTicket && (
          <Button variant="outline" onClick={() => setSelectedTicket(null)}>
            ← Back to List
          </Button>
        )}
      </div>

      {selectedTicket ? (
        <TicketDetail ticketId={selectedTicket.id} />
      ) : (
        <TicketList onSelectTicket={setSelectedTicket} />
      )}
    </div>
  );
}
