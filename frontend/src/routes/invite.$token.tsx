import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/invite/$token")({
  component: InviteComponent,
});

function InviteComponent() {
  return (
    <div className="flex flex-col items-center justify-center h-screen p-4">
      <div className="max-w-md w-full border rounded-lg p-6 shadow-sm">
        <h2 className="text-2xl font-bold mb-4 text-center">Organization Invitation</h2>
        <p className="text-center text-muted-foreground mb-6">
          You have been invited to join an organization.
        </p>
        <button
          type="button"
          className="w-full bg-primary text-primary-foreground py-2 rounded-md font-medium"
        >
          Accept Invitation
        </button>
      </div>
    </div>
  );
}
