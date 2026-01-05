import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { AppointmentStatusBadge } from './AppointmentStatusBadge';
import { formatDateTime } from '@/lib/timezone';
import { useTimezoneContext } from '@/contexts/TimezoneContext';
import { Clock, User, Stethoscope, CheckCircle, XCircle, CheckCheck } from 'lucide-react';
import type { Appointment } from '@/hooks/api/useAppointments';

interface AppointmentCardProps {
    appointment: Appointment;
    onConfirm?: (id: string) => void;
    onCancel?: (id: string) => void;
    onComplete?: (id: string) => void;
}

export function AppointmentCard({ appointment, onConfirm, onCancel, onComplete }: AppointmentCardProps) {
    const timezone = useTimezoneContext();
    const scheduledDate = new Date(appointment.scheduled_at);
    const canConfirm = appointment.status === 'SCHEDULED';
    const canCancel = ['SCHEDULED', 'CONFIRMED'].includes(appointment.status);
    const canComplete = appointment.status === 'CONFIRMED';

    return (
        <Card className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                            <AppointmentStatusBadge status={appointment.status} />
                            <span className="text-xs text-muted-foreground">
                                {appointment.appointment_type}
                            </span>
                        </div>

                        <div className="flex items-center gap-4 text-sm">
                            <div className="flex items-center gap-1.5">
                                <Clock className="h-4 w-4 text-muted-foreground" />
                                <span className="font-medium">
                                    {formatDateTime(scheduledDate, 'h:mm a', timezone)}
                                </span>
                                <span className="text-muted-foreground">
                                    ({appointment.duration_minutes} min)
                                </span>
                            </div>
                        </div>

                        <div className="flex flex-col gap-1 text-sm">
                            <div className="flex items-center gap-1.5">
                                <User className="h-4 w-4 text-muted-foreground" />
                                <span>{appointment.patient_name || 'Unknown Patient'}</span>
                            </div>
                            <div className="flex items-center gap-1.5">
                                <Stethoscope className="h-4 w-4 text-muted-foreground" />
                                <span>{appointment.provider_name || 'Unknown Provider'}</span>
                            </div>
                        </div>

                        {appointment.reason && (
                            <p className="text-sm text-muted-foreground">
                                {appointment.reason}
                            </p>
                        )}
                    </div>

                    <div className="flex flex-col gap-1">
                        {canConfirm && onConfirm && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="text-green-600 hover:text-green-700 hover:bg-green-50"
                                onClick={() => onConfirm(appointment.id)}
                            >
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Confirm
                            </Button>
                        )}
                        {canComplete && onComplete && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                onClick={() => onComplete(appointment.id)}
                            >
                                <CheckCheck className="h-4 w-4 mr-1" />
                                Complete
                            </Button>
                        )}
                        {canCancel && onCancel && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="text-destructive hover:text-destructive hover:bg-red-50"
                                onClick={() => onCancel(appointment.id)}
                            >
                                <XCircle className="h-4 w-4 mr-1" />
                                Cancel
                            </Button>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
