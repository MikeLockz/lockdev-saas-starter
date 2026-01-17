import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_auth/dashboard")({
  component: DashboardComponent,
});

function DashboardComponent() {
  return (
    <div className="p-2">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 border rounded shadow-sm">
          <h3 className="font-semibold">Organizations</h3>
          <p className="text-2xl font-bold">...</p>
        </div>
        <div className="p-4 border rounded shadow-sm">
          <h3 className="font-semibold">Patients</h3>
          <p className="text-2xl font-bold">...</p>
        </div>
        <div className="p-4 border rounded shadow-sm">
          <h3 className="font-semibold">Active Sessions</h3>
          <p className="text-2xl font-bold">...</p>
        </div>
      </div>
    </div>
  );
}
