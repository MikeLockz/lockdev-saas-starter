import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  AppointmentCreateModal,
  AppointmentList,
} from "@/components/appointments";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";

export const Route = createFileRoute("/_auth/appointments/")({
  component: AppointmentsPage,
});

function AppointmentsPage() {
  const [createModalOpen, setCreateModalOpen] = useState(false);

  return (
    <>
      <Header fixed>
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold">Appointments</h1>
        </div>
      </Header>
      <Main>
        <AppointmentList onCreate={() => setCreateModalOpen(true)} />
        <AppointmentCreateModal
          open={createModalOpen}
          onOpenChange={setCreateModalOpen}
        />
      </Main>
    </>
  );
}
