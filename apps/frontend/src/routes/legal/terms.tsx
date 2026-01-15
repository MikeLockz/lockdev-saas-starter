import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const Route = createFileRoute("/legal/terms")({
  component: TermsOfServicePage,
});

function TermsOfServicePage() {
  return (
    <div className="min-h-screen bg-muted/30">
      <header className="border-b bg-background">
        <div className="container mx-auto px-4 py-4">
          <Link to="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl">Terms of Service</CardTitle>
            <CardDescription>Last updated: January 2026</CardDescription>
          </CardHeader>
          <CardContent className="prose prose-sm dark:prose-invert max-w-none space-y-6">
            <section>
              <h2 className="text-xl font-semibold mb-3">
                1. Acceptance of Terms
              </h2>
              <p className="text-muted-foreground">
                By accessing or using Lockdev SaaS healthcare management
                platform, you agree to be bound by these Terms of Service and
                all applicable laws and regulations.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">
                2. Description of Service
              </h2>
              <p className="text-muted-foreground">
                Lockdev SaaS provides a healthcare management platform that
                enables healthcare organizations to manage patients,
                appointments, communications, and related administrative
                functions.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">
                3. User Responsibilities
              </h2>
              <p className="text-muted-foreground">You agree to:</p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                <li>Provide accurate and complete information</li>
                <li>Maintain the security of your account credentials</li>
                <li>Notify us immediately of any unauthorized access</li>
                <li>Use the service in compliance with all applicable laws</li>
                <li>
                  Not share or disclose patient health information
                  inappropriately
                </li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">
                4. Healthcare Disclaimer
              </h2>
              <p className="text-muted-foreground">
                This platform is a tool for healthcare management and
                communication. It does not provide medical advice, diagnosis, or
                treatment. Always seek the advice of qualified healthcare
                providers for medical concerns.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">
                5. Data and Privacy
              </h2>
              <p className="text-muted-foreground">
                Your use of the service is also governed by our Privacy Policy.
                We handle all Protected Health Information (PHI) in accordance
                with HIPAA requirements and applicable healthcare regulations.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">
                6. Limitation of Liability
              </h2>
              <p className="text-muted-foreground">
                To the maximum extent permitted by law, Lockdev SaaS shall not
                be liable for any indirect, incidental, special, consequential,
                or punitive damages arising from your use of the service.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">7. Modifications</h2>
              <p className="text-muted-foreground">
                We reserve the right to modify these terms at any time. We will
                notify users of significant changes via email or through the
                platform. Continued use after changes constitutes acceptance of
                the new terms.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">8. Contact</h2>
              <p className="text-muted-foreground">
                For questions about these Terms of Service, please contact us at
                legal@lockdev.com.
              </p>
            </section>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
