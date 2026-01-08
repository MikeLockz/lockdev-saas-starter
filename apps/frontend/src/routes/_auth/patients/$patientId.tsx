import { createFileRoute, useNavigate } from "@tanstack/react-router";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle,
  Mail,
  Phone,
} from "lucide-react";
import { AppointmentList } from "@/components/appointments";
import { CareTeamList } from "@/components/care-team/CareTeamList";
import { DocumentList, FileUploader } from "@/components/documents";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTimezoneContext } from "@/contexts/TimezoneContext";
import { usePatient } from "@/hooks/api/usePatients";
import { formatDateTime } from "@/lib/timezone";

export const Route = createFileRoute("/_auth/patients/$patientId")({
  component: PatientDetailPage,
});

function PatientDetailPage() {
  const timezone = useTimezoneContext();
  const navigate = useNavigate();
  const { patientId } = Route.useParams();
  const { data: patient, isLoading, error } = usePatient(patientId);

  if (isLoading) {
    return (
      <>
        <Header fixed>
          <Skeleton className="h-6 w-48" />
        </Header>
        <Main>
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        </Main>
      </>
    );
  }

  if (error || !patient) {
    return (
      <>
        <Header fixed>
          <Button variant="ghost" onClick={() => navigate({ to: "/patients" })}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Patients
          </Button>
        </Header>
        <Main>
          <div className="p-8 text-center text-destructive">
            Error loading patient: {error?.message || "Patient not found"}
          </div>
        </Main>
      </>
    );
  }

  return (
    <>
      <Header fixed>
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate({ to: "/patients" })}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-lg font-semibold">
              {patient.last_name}, {patient.first_name}
            </h1>
            <p className="text-sm text-muted-foreground">
              MRN: {patient.medical_record_number || "N/A"}
            </p>
          </div>
        </div>
      </Header>
      <Main>
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="contacts">Contacts</TabsTrigger>
            <TabsTrigger value="care-team">Care Team</TabsTrigger>
            <TabsTrigger value="appointments">Appointments</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="messages">Messages</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Patient Information</CardTitle>
                <CardDescription>
                  Basic demographics and enrollment details
                </CardDescription>
              </CardHeader>
              <CardContent>
                <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">
                      Date of Birth
                    </dt>
                    <dd className="text-sm">
                      {formatDateTime(
                        new Date(patient.dob),
                        "MMMM d, yyyy",
                        timezone,
                      )}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">
                      Legal Sex
                    </dt>
                    <dd className="text-sm">
                      {patient.legal_sex || "Not specified"}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">
                      MRN
                    </dt>
                    <dd className="text-sm font-mono">
                      {patient.medical_record_number || "—"}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">
                      Status
                    </dt>
                    <dd>
                      <Badge variant="default">
                        {patient.subscription_status}
                      </Badge>
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-muted-foreground">
                      Enrolled
                    </dt>
                    <dd className="text-sm">
                      {patient.enrolled_at
                        ? formatDateTime(
                            new Date(patient.enrolled_at),
                            "MMMM d, yyyy",
                            timezone,
                          )
                        : "—"}
                    </dd>
                  </div>
                </dl>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="contacts" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Contact Methods</CardTitle>
                <CardDescription>
                  Phone, email, and communication preferences
                </CardDescription>
              </CardHeader>
              <CardContent>
                {patient.contact_methods.length === 0 ? (
                  <p className="text-muted-foreground text-sm">
                    No contact methods on file.
                  </p>
                ) : (
                  <div className="space-y-3">
                    {patient.contact_methods.map((contact) => (
                      <div
                        key={contact.id}
                        className="flex items-center justify-between p-3 rounded-lg border"
                      >
                        <div className="flex items-center gap-3">
                          {contact.type === "EMAIL" ? (
                            <Mail className="h-4 w-4 text-muted-foreground" />
                          ) : (
                            <Phone className="h-4 w-4 text-muted-foreground" />
                          )}
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-medium">
                                {contact.value}
                              </span>
                              {contact.is_primary && (
                                <Badge variant="secondary" className="text-xs">
                                  Primary
                                </Badge>
                              )}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {contact.label || contact.type}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {contact.is_safe_for_voicemail ? (
                            <div className="flex items-center gap-1 text-xs text-green-600">
                              <CheckCircle className="h-3 w-3" />
                              Safe for voicemail
                            </div>
                          ) : (
                            <div className="flex items-center gap-1 text-xs text-amber-600">
                              <AlertTriangle className="h-3 w-3" />
                              No voicemail
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="care-team" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Care Team</CardTitle>
                <CardDescription>
                  Providers assigned to this patient
                </CardDescription>
              </CardHeader>
              <CardContent>
                <CareTeamList patientId={patientId} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appointments" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Appointments</CardTitle>
                <CardDescription>
                  Patient's scheduled appointments
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AppointmentList patientId={patientId} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documents" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Upload Document</CardTitle>
                <CardDescription>
                  Upload patient documents to secure storage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileUploader patientId={patientId} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Documents</CardTitle>
                <CardDescription>Patient's uploaded documents</CardDescription>
              </CardHeader>
              <CardContent>
                <DocumentList patientId={patientId} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="messages">
            <Card>
              <CardHeader>
                <CardTitle>Messages</CardTitle>
                <CardDescription>
                  Communicate with this patient securely.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-muted-foreground">
                  <div className="flex justify-center mb-4">
                    <Mail className="h-12 w-12 opacity-20" />
                  </div>
                  <p>No messages yet.</p>
                  <Button variant="outline" className="mt-4">
                    Start New Conversation
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </Main>
    </>
  );
}
