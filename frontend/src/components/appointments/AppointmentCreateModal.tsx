import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { format } from 'date-fns';
import { useCreateAppointment } from '@/hooks/api/useAppointments';
import { usePatients } from '@/hooks/api/usePatients';
import { useProviders } from '@/hooks/useProviders';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from '@/components/ui/command';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';
import { toast } from 'sonner';
import { Check, ChevronsUpDown, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AppointmentCreateModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    defaultPatientId?: string;
    defaultDate?: Date;
}

interface FormData {
    patient_id: string;
    provider_id: string;
    scheduled_date: string;
    scheduled_time: string;
    duration_minutes: number;
    appointment_type: string;
    reason: string;
}

const APPOINTMENT_TYPES = [
    { value: 'INITIAL_CONSULT', label: 'Initial Consultation' },
    { value: 'FOLLOW_UP', label: 'Follow-up' },
    { value: 'URGENT', label: 'Urgent Visit' },
    { value: 'ROUTINE', label: 'Routine Check-up' },
    { value: 'PROCEDURE', label: 'Procedure' },
];

const DURATION_OPTIONS = [
    { value: 15, label: '15 minutes' },
    { value: 30, label: '30 minutes' },
    { value: 45, label: '45 minutes' },
    { value: 60, label: '1 hour' },
    { value: 90, label: '1.5 hours' },
];

export function AppointmentCreateModal({
    open,
    onOpenChange,
    defaultPatientId,
    defaultDate,
}: AppointmentCreateModalProps) {
    const [patientSearch, setPatientSearch] = useState('');
    const [patientOpen, setPatientOpen] = useState(false);
    const [selectedPatientName, setSelectedPatientName] = useState('');

    const createAppointment = useCreateAppointment();
    const { data: patients, isLoading: patientsLoading } = usePatients({ name: patientSearch, limit: 10 });
    const { data: providers } = useProviders({ isActive: true });

    const { register, handleSubmit, setValue, watch, reset, formState: { errors } } = useForm<FormData>({
        defaultValues: {
            patient_id: defaultPatientId || '',
            provider_id: '',
            scheduled_date: defaultDate ? format(defaultDate, 'yyyy-MM-dd') : format(new Date(), 'yyyy-MM-dd'),
            scheduled_time: '09:00',
            duration_minutes: 30,
            appointment_type: 'FOLLOW_UP',
            reason: '',
        },
    });

    const watchPatientId = watch('patient_id');

    useEffect(() => {
        if (defaultPatientId && open) {
            setValue('patient_id', defaultPatientId);
        }
    }, [defaultPatientId, open, setValue]);

    useEffect(() => {
        if (!open) {
            reset();
            setSelectedPatientName('');
            setPatientSearch('');
        }
    }, [open, reset]);

    const onSubmit = async (data: FormData) => {
        try {
            const scheduled_at = new Date(`${data.scheduled_date}T${data.scheduled_time}`).toISOString();
            await createAppointment.mutateAsync({
                patient_id: data.patient_id,
                provider_id: data.provider_id,
                scheduled_at,
                duration_minutes: data.duration_minutes,
                appointment_type: data.appointment_type,
                reason: data.reason || undefined,
            });
            toast.success('Appointment created successfully');
            onOpenChange(false);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to create appointment';
            toast.error(message);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Schedule Appointment</DialogTitle>
                    <DialogDescription>
                        Create a new appointment for a patient.
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    {/* Patient Selector */}
                    <div className="space-y-2">
                        <Label htmlFor="patient">Patient *</Label>
                        {defaultPatientId ? (
                            <Input value={selectedPatientName || 'Selected Patient'} disabled />
                        ) : (
                            <Popover open={patientOpen} onOpenChange={setPatientOpen}>
                                <PopoverTrigger asChild>
                                    <Button
                                        variant="outline"
                                        role="combobox"
                                        aria-expanded={patientOpen}
                                        className="w-full justify-between"
                                    >
                                        {selectedPatientName || 'Select patient...'}
                                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                    </Button>
                                </PopoverTrigger>
                                <PopoverContent className="w-[400px] p-0">
                                    <Command shouldFilter={false}>
                                        <CommandInput
                                            placeholder="Search patients..."
                                            value={patientSearch}
                                            onValueChange={setPatientSearch}
                                        />
                                        <CommandList>
                                            {patientsLoading ? (
                                                <div className="flex items-center justify-center py-6">
                                                    <Loader2 className="h-4 w-4 animate-spin" />
                                                </div>
                                            ) : (
                                                <>
                                                    <CommandEmpty>No patients found.</CommandEmpty>
                                                    <CommandGroup>
                                                        {patients?.items.map((patient) => (
                                                            <CommandItem
                                                                key={patient.id}
                                                                value={patient.id}
                                                                onSelect={() => {
                                                                    setValue('patient_id', patient.id);
                                                                    setSelectedPatientName(`${patient.last_name}, ${patient.first_name}`);
                                                                    setPatientOpen(false);
                                                                }}
                                                            >
                                                                <Check
                                                                    className={cn(
                                                                        "mr-2 h-4 w-4",
                                                                        watchPatientId === patient.id ? "opacity-100" : "opacity-0"
                                                                    )}
                                                                />
                                                                <div>
                                                                    <div>{patient.last_name}, {patient.first_name}</div>
                                                                    <div className="text-xs text-muted-foreground">
                                                                        DOB: {format(new Date(patient.dob), 'MM/dd/yyyy')}
                                                                        {patient.medical_record_number && ` • MRN: ${patient.medical_record_number}`}
                                                                    </div>
                                                                </div>
                                                            </CommandItem>
                                                        ))}
                                                    </CommandGroup>
                                                </>
                                            )}
                                        </CommandList>
                                    </Command>
                                </PopoverContent>
                            </Popover>
                        )}
                        {errors.patient_id && (
                            <p className="text-sm text-destructive">Patient is required</p>
                        )}
                    </div>

                    {/* Provider Selector */}
                    <div className="space-y-2">
                        <Label htmlFor="provider">Provider *</Label>
                        <Select onValueChange={(val) => setValue('provider_id', val)}>
                            <SelectTrigger>
                                <SelectValue placeholder="Select provider" />
                            </SelectTrigger>
                            <SelectContent>
                                {providers?.items.map((provider) => (
                                    <SelectItem key={provider.id} value={provider.id}>
                                        {provider.user_display_name || provider.user_email}
                                        {provider.specialty && ` (${provider.specialty})`}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        {errors.provider_id && (
                            <p className="text-sm text-destructive">Provider is required</p>
                        )}
                    </div>

                    {/* Date and Time */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="scheduled_date">Date *</Label>
                            <Input
                                type="date"
                                {...register('scheduled_date', { required: true })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="scheduled_time">Time *</Label>
                            <Input
                                type="time"
                                {...register('scheduled_time', { required: true })}
                            />
                        </div>
                    </div>

                    {/* Duration and Type */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="duration">Duration</Label>
                            <Select
                                defaultValue="30"
                                onValueChange={(val) => setValue('duration_minutes', parseInt(val))}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {DURATION_OPTIONS.map((opt) => (
                                        <SelectItem key={opt.value} value={String(opt.value)}>
                                            {opt.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="type">Type</Label>
                            <Select
                                defaultValue="FOLLOW_UP"
                                onValueChange={(val) => setValue('appointment_type', val)}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {APPOINTMENT_TYPES.map((type) => (
                                        <SelectItem key={type.value} value={type.value}>
                                            {type.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Reason */}
                    <div className="space-y-2">
                        <Label htmlFor="reason">Reason</Label>
                        <Textarea
                            {...register('reason')}
                            placeholder="Brief description of the appointment reason"
                            rows={3}
                        />
                    </div>

                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={createAppointment.isPending}>
                            {createAppointment.isPending && (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            )}
                            Schedule
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
