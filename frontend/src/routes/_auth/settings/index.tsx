import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_auth/settings/")({
  component: SettingsComponent,
});

function SettingsComponent() {
  return (
    <div className="p-2">
      <h2 className="text-2xl font-bold">Settings</h2>
      <div className="mt-4">
        <p>Manage your account settings and security preferences.</p>
      </div>
    </div>
  );
}
