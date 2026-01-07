import { createFileRoute } from "@tanstack/react-router";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { PatientTable } from "@/components/patients/PatientTable";

export const Route = createFileRoute("/_auth/patients/")({
  component: PatientsPage,
});

function PatientsPage() {
  return (
    <>
      <Header fixed>
        <h1 className="text-lg font-semibold">Patients</h1>
      </Header>
      <Main>
        <PatientTable />
      </Main>
    </>
  );
}
