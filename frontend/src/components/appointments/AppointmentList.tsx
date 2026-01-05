import { useState, useMemo } from 'react';
import { startOfDay, endOfDay, addDays } from 'date-fns';
import { formatDateTime } from '@/lib/timezone';
import { useTimezoneContext } from '@/contexts/TimezoneContext';
import { useAppointments, useUpdateAppointmentStatus } from '@/hooks/api/useAppointments';
import { useProviders } from '@/hooks/useProviders';
import { AppointmentCard } from './AppointmentCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Calendar, ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { toast } from 'sonner';

interface AppointmentListProps {
    patientId?: string;
    onCreate?: () => void;
}

export function AppointmentList({ patientId, onCreate }: AppointmentListProps) {
    const timezone = useTimezoneContext();
    const [selectedDate, setSelectedDate] = useState<Date>(new Date());
    const [providerFilter, setProviderFilter] = useState<string>('all');
    const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
    const [appointmentToCancel, setAppointmentToCancel] = useState<string | null>(null);
    const [cancellationReason, setCancellationReason] = useState('');

    const dateFrom = formatDateTime(startOfDay(selectedDate), "yyyy-MM-dd'T'HH:mm:ss", 'UTC');
    const dateTo = formatDateTime(endOfDay(selectedDate), "yyyy-MM-dd'T'HH:mm:ss", 'UTC');

    const { data: appointments, isLoading, error, refetch } = useAppointments({
        date_from: dateFrom,
        date_to: dateTo,
        provider_id: providerFilter !== 'all' ? providerFilter : undefined,
        patient_id: patientId,
    });

    const { data: providers } = useProviders({ isActive: true });
    const updateStatus = useUpdateAppointmentStatus();

    const sortedAppointments = useMemo(() => {
        if (!appointments?.items) return [];
        return [...appointments.items].sort((a, b) =>
            new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime()
        );
    }, [appointments]);

    const handlePreviousDay = () => setSelectedDate((d) => addDays(d, -1));
    const handleNextDay = () => setSelectedDate((d) => addDays(d, 1));
    const handleToday = () => setSelectedDate(new Date());

    const handleConfirm = async (appointmentId: string) => {
        try {
            await updateStatus.mutateAsync({ appointmentId, data: { status: 'CONFIRMED' } });
            toast.success('Appointment confirmed');
        } catch {
            toast.error('Failed to confirm appointment');
        }
    };

    const handleComplete = async (appointmentId: string) => {
        try {
            await updateStatus.mutateAsync({ appointmentId, data: { status: 'COMPLETED' } });
            toast.success('Appointment marked as completed');
        } catch {
            toast.error('Failed to complete appointment');
        }
    };

    const handleCancelClick = (appointmentId: string) => {
        setAppointmentToCancel(appointmentId);
        setCancellationReason('');
        setCancelDialogOpen(true);
    };

    const handleCancelConfirm = async () => {
        if (!appointmentToCancel) return;
        try {
            await updateStatus.mutateAsync({
                appointmentId: appointmentToCancel,
                data: { status: 'CANCELLED', cancellation_reason: cancellationReason || undefined },
            });
            toast.success('Appointment cancelled');
            setCancelDialogOpen(false);
            setAppointmentToCancel(null);
        } catch {
            toast.error('Failed to cancel appointment');
        }
    };

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-center">
                <p className="text-muted-foreground mb-4">Failed to load appointments</p>
                <Button variant="outline" onClick={() => refetch()}>
                    Retry
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Filters */}
            <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="icon" onClick={handlePreviousDay}>
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" onClick={handleToday}>
                        <Calendar className="h-4 w-4 mr-2" />
                        {formatDateTime(selectedDate, 'EEEE, MMMM d, yyyy', timezone)}
                    </Button>
                    <Button variant="outline" size="icon" onClick={handleNextDay}>
                        <ChevronRight className="h-4 w-4" />
                    </Button>
                </div>

                <Select value={providerFilter} onValueChange={setProviderFilter}>
                    <SelectTrigger className="w-[200px]">
                        <SelectValue placeholder="Filter by provider" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Providers</SelectItem>
                        {providers?.items.map((provider) => (
                            <SelectItem key={provider.id} value={provider.id}>
                                {provider.user_display_name || provider.user_email}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>

                {onCreate && (
                    <Button onClick={onCreate} className="ml-auto">
                        <Plus className="h-4 w-4 mr-2" />
                        New Appointment
                    </Button>
                )}
            </div>

            {/* Appointment List */}
            {isLoading ? (
                <div className="space-y-3">
                    {[...Array(3)].map((_, i) => (
                        <Skeleton key={i} className="h-32 w-full" />
                    ))}
                </div>
            ) : sortedAppointments.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg">
                    <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium">No appointments</h3>
                    <p className="text-muted-foreground">
                        No appointments scheduled for {formatDateTime(selectedDate, 'MMMM d, yyyy', timezone)}
                    </p>
                    {onCreate && (
                        <Button onClick={onCreate} className="mt-4">
                            <Plus className="h-4 w-4 mr-2" />
                            Schedule Appointment
                        </Button>
                    )}
                </div>
            ) : (
                <div className="space-y-3">
                    {sortedAppointments.map((apt) => (
                        <AppointmentCard
                            key={apt.id}
                            appointment={apt}
                            onConfirm={handleConfirm}
                            onCancel={handleCancelClick}
                            onComplete={handleComplete}
                        />
                    ))}
                </div>
            )}

            {/* Cancel Dialog */}
            <AlertDialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Cancel Appointment</AlertDialogTitle>
                        <AlertDialogDescription>
                            Are you sure you want to cancel this appointment? This action cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <div className="py-4">
                        <Input
                            placeholder="Reason for cancellation (optional)"
                            value={cancellationReason}
                            onChange={(e) => setCancellationReason(e.target.value)}
                        />
                    </div>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Keep Appointment</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleCancelConfirm}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                            Cancel Appointment
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
