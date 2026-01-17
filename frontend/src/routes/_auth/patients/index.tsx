import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_auth/patients/")({
  component: PatientsComponent,
});

function PatientsComponent() {
  return (
    <div className="p-2">
      <h2 className="text-2xl font-bold">Patients</h2>
      <div className="mt-4">
        <p>Manage your patient records here.</p>
      </div>
    </div>
  );
}
