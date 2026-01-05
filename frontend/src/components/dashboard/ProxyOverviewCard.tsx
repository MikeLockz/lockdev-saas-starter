import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { useMyProxyPatients, type ProxyPatient } from '@/hooks/api/useMyProxyPatients';
import { Users, Calendar, Eye, MessageSquare, FileText } from 'lucide-react';

interface ProxyOverviewCardProps {
    proxyId: string;
}

/**
 * Dashboard card for proxy users showing their assigned patients
 * and quick action buttons.
 */
export function ProxyOverviewCard({ proxyId: _proxyId }: ProxyOverviewCardProps) {
    const { data: patients, isLoading, error } = useMyProxyPatients();

    if (isLoading) {
        return (
            <Card className="lg:col-span-4">
                <CardHeader>
                    <Skeleton className="h-6 w-32" />
                    <Skeleton className="h-4 w-48" />
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {[1, 2].map((i) => (
                            <div key={i} className="flex items-center gap-4 p-4 border rounded-lg">
                                <Skeleton className="h-10 w-10 rounded-full" />
                                <div className="flex-1 space-y-2">
                                    <Skeleton className="h-4 w-32" />
                                    <Skeleton className="h-3 w-24" />
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="lg:col-span-4">
                <CardHeader>
                    <CardTitle>My Patients</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center text-destructive py-8">
                        Failed to load patients. Please try again.
                    </div>
                </CardContent>
            </Card>
        );
    }

    const getPermissionSummary = (patient: ProxyPatient) => {
        const perms = patient.permissions;
        const enabledCount = [
            perms.can_view_profile,
            perms.can_view_appointments,
            perms.can_schedule_appointments,
            perms.can_view_clinical_notes,
            perms.can_view_billing,
            perms.can_message_providers,
        ].filter(Boolean).length;
        return `${enabledCount} of 6 permissions`;
    };

    const relationshipLabels: Record<string, string> = {
        PARENT: 'Parent',
        SPOUSE: 'Spouse',
        GUARDIAN: 'Guardian',
        CAREGIVER: 'Caregiver',
        POA: 'Power of Attorney',
        OTHER: 'Other',
    };

    return (
        <Card className="lg:col-span-4">
            <CardHeader className="flex flex-row items-center justify-between">
                <div>
                    <CardTitle className="flex items-center gap-2">
                        <Users className="h-5 w-5" />
                        My Patients
                    </CardTitle>
                    <CardDescription>
                        Patients you're authorized to manage
                    </CardDescription>
                </div>
                <a href="/proxy/patients">
                    <Button variant="outline" size="sm">View All</Button>
                </a>
            </CardHeader>
            <CardContent>
                {patients && patients.length > 0 ? (
                    <div className="space-y-4">
                        {patients.map((proxyPatient) => (
                            <div
                                key={proxyPatient.patient.id}
                                className="flex items-center gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                            >
                                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                                    <span className="text-lg font-semibold">
                                        {proxyPatient.patient.first_name.charAt(0)}
                                        {proxyPatient.patient.last_name.charAt(0)}
                                    </span>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <p className="font-medium truncate">
                                            {proxyPatient.patient.first_name} {proxyPatient.patient.last_name}
                                        </p>
                                        <Badge variant="secondary" className="text-xs">
                                            {relationshipLabels[proxyPatient.relationship_type] || proxyPatient.relationship_type}
                                        </Badge>
                                    </div>
                                    <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                                        <span>DOB: {new Date(proxyPatient.patient.dob).toLocaleDateString()}</span>
                                        {proxyPatient.patient.medical_record_number && (
                                            <span>MRN: {proxyPatient.patient.medical_record_number}</span>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-1 mt-2">
                                        {proxyPatient.permissions.can_view_profile && (
                                            <Eye className="h-3.5 w-3.5 text-muted-foreground" />
                                        )}
                                        {proxyPatient.permissions.can_view_appointments && (
                                            <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                                        )}
                                        {proxyPatient.permissions.can_message_providers && (
                                            <MessageSquare className="h-3.5 w-3.5 text-muted-foreground" />
                                        )}
                                        {proxyPatient.permissions.can_view_clinical_notes && (
                                            <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                                        )}
                                        <span className="text-xs text-muted-foreground ml-2">
                                            {getPermissionSummary(proxyPatient)}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex gap-2 shrink-0">
                                    {proxyPatient.permissions.can_view_appointments && (
                                        <Button variant="ghost" size="sm">
                                            <Calendar className="h-4 w-4 mr-1" />
                                            Appointments
                                        </Button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-12 text-muted-foreground">
                        <Users className="mx-auto h-12 w-12 mb-4 opacity-50" />
                        <p>No patients assigned</p>
                        <p className="text-sm">
                            Contact your healthcare provider to set up proxy access.
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
