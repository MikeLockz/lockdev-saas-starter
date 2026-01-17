import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/consent")({
  component: ConsentComponent,
});

function ConsentComponent() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="max-w-2xl w-full border rounded-lg p-8 shadow-md bg-card">
        <h2 className="text-3xl font-bold mb-6 text-center">Terms and Consent</h2>
        <p className="mb-8 text-muted-foreground text-center">
          Please review and accept the following documents to continue using the platform.
        </p>

        <div className="space-y-6">
          {/* Document list would go here */}
          <div className="p-4 border rounded bg-muted/50">
            <h3 className="font-semibold mb-2">Terms of Service</h3>
            <p className="text-sm text-muted-foreground">Version 1.0 - Last Updated: Jan 2026</p>
          </div>

          <div className="p-4 border rounded bg-muted/50">
            <h3 className="font-semibold mb-2">HIPAA Patient Consent</h3>
            <p className="text-sm text-muted-foreground">Version 1.0 - Last Updated: Jan 2026</p>
          </div>
        </div>

        <button
          type="button"
          className="w-full mt-8 bg-primary text-primary-foreground py-3 rounded-md font-bold text-lg hover:opacity-90 transition-opacity"
        >
          I Agree to All Terms
        </button>
      </div>
    </div>
  );
}
