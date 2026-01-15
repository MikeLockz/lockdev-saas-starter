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

export const Route = createFileRoute("/legal/privacy")({
  component: PrivacyPolicyPage,
});

function PrivacyPolicyPage() {
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
            <CardTitle className="text-3xl">Privacy Policy</CardTitle>
            <CardDescription>Last updated: January 2026</CardDescription>
          </CardHeader>
          <CardContent className="prose prose-sm dark:prose-invert max-w-none space-y-6">
            <section>
              <h2 className="text-xl font-semibold mb-3">1. Introduction</h2>
              <p className="text-muted-foreground">
                This Privacy Policy describes how Lockdev SaaS ("we", "our", or
                "us") collects, uses, and shares information about you when you
                use our healthcare management platform and related services.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">
                2. Information We Collect
              </h2>
              <p className="text-muted-foreground">
                We collect information you provide directly, including:
              </p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                <li>Account information (name, email, password)</li>
                <li>Profile information</li>
                <li>Health-related data you provide</li>
                <li>Communications with healthcare providers</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">
                3. HIPAA Compliance
              </h2>
              <p className="text-muted-foreground">
                We are committed to protecting your Protected Health Information
                (PHI) in accordance with the Health Insurance Portability and
                Accountability Act (HIPAA). We implement appropriate safeguards
                to protect PHI and limit its use and disclosure.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">
                4. How We Use Your Information
              </h2>
              <p className="text-muted-foreground">
                We use the information we collect to:
              </p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                <li>Provide and improve our services</li>
                <li>Facilitate communication with healthcare providers</li>
                <li>Manage appointments and healthcare records</li>
                <li>Send important notifications and updates</li>
                <li>Comply with legal obligations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">5. Data Security</h2>
              <p className="text-muted-foreground">
                We implement industry-standard security measures including
                encryption, access controls, and audit logging to protect your
                information. All data is transmitted securely and stored in
                compliance with healthcare regulations.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">6. Your Rights</h2>
              <p className="text-muted-foreground">You have the right to:</p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-1">
                <li>Access your personal information</li>
                <li>Request correction of inaccurate data</li>
                <li>
                  Request deletion of your data (subject to legal requirements)
                </li>
                <li>Receive a copy of your health records</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-3">7. Contact Us</h2>
              <p className="text-muted-foreground">
                If you have questions about this Privacy Policy or our data
                practices, please contact our Privacy Officer at
                privacy@lockdev.com.
              </p>
            </section>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
