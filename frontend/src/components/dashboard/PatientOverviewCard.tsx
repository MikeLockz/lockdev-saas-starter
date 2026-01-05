import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { usePatientUpcomingAppointments } from '@/hooks/api/useDashboardStats';
import { useCareTeam, type CareTeamMember } from '@/hooks/useCareTeam';
import { Calendar, Clock, Users, User, Stethoscope } from 'lucide-react';

interface PatientOverviewCardProps {
    patientId: string | undefined;
}

/**
 * Patient Overview Card displays:
 * - Upcoming appointments (next 3)
 * - Care team contacts
 */
export function PatientOverviewCard({ patientId }: PatientOverviewCardProps) {
    const { data: appointments, isLoading: isApptLoading } = usePatientUpcomingAppointments(patientId);
    const { data: careTeam, isLoading: isCareTeamLoading } = useCareTeam(patientId);

    const isLoading = isApptLoading || isCareTeamLoading;

    const formatDateTime = (dateStr: string) => {
        const date = new Date(dateStr);
        const dateFormatted = date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        });
        const timeFormatted = date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
        return { date: dateFormatted, time: timeFormatted };
    };

    const getRoleColor = (role: string) => {
        switch (role) {
            case 'PRIMARY':
                return 'default';
            case 'SPECIALIST':
                return 'secondary';
            case 'CONSULTANT':
                return 'outline';
            default:
                return 'outline';
        }
    };

    if (isLoading) {
        return (
            <Card className="lg:col-span-4">
                <CardHeader>
                    <CardTitle>My Healthcare</CardTitle>
                    <CardDescription>Loading your appointments and care team...</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="flex items-center gap-4">
                            <Skeleton className="h-10 w-16" />
                            <div className="flex-1 space-y-1">
                                <Skeleton className="h-4 w-32" />
                                <Skeleton className="h-3 w-24" />
                            </div>
                        </div>
                    ))}
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="lg:col-span-4">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <Calendar className="h-5 w-5" />
                            My Healthcare
                        </CardTitle>
                        <CardDescription>
                            {appointments?.length || 0} upcoming appointments
                        </CardDescription>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {/* Upcoming Appointments */}
                    {appointments && appointments.length > 0 ? (
                        <div className="space-y-3">
                            <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                <Clock className="h-4 w-4" />
                                Upcoming Appointments
                            </h4>
                            <div className="space-y-2">
                                {appointments.map((appt) => {
                                    const { date, time } = formatDateTime(appt.scheduled_at);
                                    return (
                                        <div
                                            key={appt.id}
                                            className="flex items-center gap-3 py-2 px-3 rounded-md bg-muted/50 hover:bg-muted/80 transition-colors"
                                        >
                                            <div className="text-center min-w-[70px]">
                                                <div className="text-xs text-muted-foreground">{date}</div>
                                                <div className="text-sm font-medium text-primary">{time}</div>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2">
                                                    <Stethoscope className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                                                    <span className="text-sm font-medium truncate">
                                                        {appt.provider_name || 'Provider'}
                                                    </span>
                                                </div>
                                                {appt.reason && (
                                                    <p className="text-xs text-muted-foreground truncate mt-0.5">
                                                        {appt.reason}
                                                    </p>
                                                )}
                                            </div>
                                            <Badge variant="outline" className="text-xs flex-shrink-0">
                                                {appt.appointment_type?.toLowerCase().replace('_', ' ') || 'Visit'}
                                            </Badge>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-6 text-muted-foreground">
                            <Calendar className="h-10 w-10 mb-2 opacity-50" />
                            <p className="text-sm">No upcoming appointments</p>
                            <p className="text-xs">Schedule your next visit</p>
                        </div>
                    )}

                    {/* Care Team */}
                    {careTeam && careTeam.members && careTeam.members.length > 0 && (
                        <div className="pt-3 border-t">
                            <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2 mb-2">
                                <Users className="h-4 w-4" />
                                My Care Team
                            </h4>
                            <div className="grid grid-cols-1 gap-2">
                                {careTeam.members.slice(0, 3).map((member: CareTeamMember) => (
                                    <div
                                        key={member.assignment_id}
                                        className="flex items-center gap-3 p-2 rounded-md bg-muted/30 border border-muted"
                                    >
                                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                                            <User className="h-4 w-4 text-primary" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium truncate">
                                                {member.provider_name || 'Provider'}
                                            </p>
                                            <p className="text-xs text-muted-foreground truncate">
                                                {member.provider_specialty || 'General'}
                                            </p>
                                        </div>
                                        <Badge variant={getRoleColor(member.role)} className="text-[10px] px-1.5">
                                            {member.role}
                                        </Badge>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
