import { Link } from "@tanstack/react-router";
import { Calendar, Eye, MessageSquare, User } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ProxyPatient } from "@/hooks/api/useMyProxyPatients";

const RELATIONSHIP_LABELS: Record<string, string> = {
  PARENT: "Parent",
  SPOUSE: "Spouse",
  GUARDIAN: "Guardian",
  CAREGIVER: "Caregiver",
  POA: "Power of Attorney",
  OTHER: "Other",
};

interface ProxyPatientCardProps {
  proxyPatient: ProxyPatient;
}

export function ProxyPatientCard({ proxyPatient }: ProxyPatientCardProps) {
  const { patient, relationship_type, permissions } = proxyPatient;
  const fullName = `${patient.first_name} ${patient.last_name}`;

  const quickActions = [
    {
      key: "profile",
      label: "Profile",
      icon: User,
      enabled: permissions.can_view_profile,
    },
    {
      key: "appointments",
      label: "Appointments",
      icon: Calendar,
      enabled: permissions.can_view_appointments,
    },
    {
      key: "records",
      label: "Records",
      icon: Eye,
      enabled: permissions.can_view_clinical_notes,
    },
    {
      key: "messages",
      label: "Messages",
      icon: MessageSquare,
      enabled: permissions.can_message_providers,
    },
  ];

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">{fullName}</CardTitle>
          <Badge variant="secondary">
            {RELATIONSHIP_LABELS[relationship_type] || relationship_type}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          DOB: {new Date(patient.dob).toLocaleDateString()}
          {patient.medical_record_number &&
            ` • MRN: ${patient.medical_record_number}`}
        </p>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2 mb-4">
          {quickActions
            .filter((a) => a.enabled)
            .map((action) => (
              <Button key={action.key} variant="outline" size="sm" asChild>
                <Link
                  to="/patients/$patientId"
                  params={{ patientId: patient.id }}
                >
                  <action.icon className="mr-1.5 h-3.5 w-3.5" />
                  {action.label}
                </Link>
              </Button>
            ))}
        </div>
        <Button className="w-full" asChild>
          <Link to="/patients/$patientId" params={{ patientId: patient.id }}>
            View Details
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
