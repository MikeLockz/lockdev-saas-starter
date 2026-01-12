import { format } from "date-fns";
import { Check, ChevronsUpDown, Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useCreateAppointment } from "@/hooks/api/useAppointments";
import { useMyProxyPatients } from "@/hooks/api/useMyProxyPatients";
import { usePatients } from "@/hooks/api/usePatients";
import { useProviders } from "@/hooks/useProviders";
import { useUserRole } from "@/hooks/useUserRole";
import { cn } from "@/lib/utils";

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

interface PatientOption {
  id: string;
  firstName: string;
  lastName: string;
  dob: string;
  mrn: string | null;
}

const APPOINTMENT_TYPES = [
  { value: "INITIAL_CONSULT", label: "Initial Consultation" },
  { value: "FOLLOW_UP", label: "Follow-up" },
  { value: "URGENT", label: "Urgent Visit" },
  { value: "ROUTINE", label: "Routine Check-up" },
  { value: "PROCEDURE", label: "Procedure" },
];

const DURATION_OPTIONS = [
  { value: 15, label: "15 minutes" },
  { value: 30, label: "30 minutes" },
  { value: 45, label: "45 minutes" },
  { value: 60, label: "1 hour" },
  { value: 90, label: "1.5 hours" },
];

export function AppointmentCreateModal({
  open,
  onOpenChange,
  defaultPatientId,
  defaultDate,
}: AppointmentCreateModalProps) {
  const [patientSearch, setPatientSearch] = useState("");
  const [patientOpen, setPatientOpen] = useState(false);
  const [selectedPatientName, setSelectedPatientName] = useState("");

  const { roleInfo, isLoading: isRoleLoading } = useUserRole();
  const createAppointment = useCreateAppointment();

  // For staff/provider/admin: use regular patients API
  const { data: allPatients, isLoading: patientsLoading } = usePatients({
    name: patientSearch,
    limit: 10,
  });

  // For proxy users: use proxy-patients API (only authorized patients)
  const { data: proxyPatients, isLoading: proxyPatientsLoading } =
    useMyProxyPatients();

  const { data: providers } = useProviders({ isActive: true });

  // Determine available patients based on role
  const patientOptions = useMemo<PatientOption[]>(() => {
    if (!roleInfo) return [];

    // Patient role: only themselves (handled separately - no dropdown)
    if (roleInfo.role === "patient") {
      return [];
    }

    // Proxy role: only their authorized patients
    if (roleInfo.role === "proxy" && proxyPatients) {
      return proxyPatients
        .filter((pp) => pp.permissions.can_schedule_appointments)
        .map((pp) => ({
          id: pp.patient.id,
          firstName: pp.patient.first_name,
          lastName: pp.patient.last_name,
          dob: pp.patient.dob,
          mrn: pp.patient.medical_record_number,
        }));
    }

    // Staff/Provider/Admin: use regular patients list
    if (allPatients?.items) {
      return allPatients.items.map((p) => ({
        id: p.id,
        firstName: p.first_name,
        lastName: p.last_name,
        dob: p.dob,
        mrn: p.medical_record_number,
      }));
    }

    return [];
  }, [roleInfo, proxyPatients, allPatients]);

  // Determine if we should show the patient selector
  const showPatientSelector = useMemo(() => {
    if (!roleInfo) return false;
    // Patients book for themselves - no selector needed
    if (roleInfo.role === "patient") return false;
    // Proxies need selector if they have multiple authorized patients
    if (roleInfo.role === "proxy") return patientOptions.length > 0;
    // Staff/Providers/Admins always see selector
    return true;
  }, [roleInfo, patientOptions]);

  const isPatientListLoading =
    roleInfo?.role === "proxy" ? proxyPatientsLoading : patientsLoading;

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      patient_id: defaultPatientId || "",
      provider_id: "",
      scheduled_date: defaultDate
        ? format(defaultDate, "yyyy-MM-dd")
        : format(new Date(), "yyyy-MM-dd"),
      scheduled_time: "09:00",
      duration_minutes: 30,
      appointment_type: "FOLLOW_UP",
      reason: "",
    },
  });

  const watchPatientId = watch("patient_id");

  // Auto-set patient_id for patient role
  useEffect(() => {
    if (roleInfo?.role === "patient" && roleInfo.patientId && open) {
      setValue("patient_id", roleInfo.patientId);
      setSelectedPatientName("You");
    }
  }, [roleInfo, open, setValue]);

  // Auto-select single proxy patient
  useEffect(() => {
    if (
      roleInfo?.role === "proxy" &&
      patientOptions.length === 1 &&
      open &&
      !watchPatientId
    ) {
      const patient = patientOptions[0];
      setValue("patient_id", patient.id);
      setSelectedPatientName(`${patient.lastName}, ${patient.firstName}`);
    }
  }, [roleInfo, patientOptions, open, setValue, watchPatientId]);

  useEffect(() => {
    if (defaultPatientId && open) {
      setValue("patient_id", defaultPatientId);
    }
  }, [defaultPatientId, open, setValue]);

  useEffect(() => {
    if (!open) {
      reset();
      setSelectedPatientName("");
      setPatientSearch("");
    }
  }, [open, reset]);

  const onSubmit = async (data: FormData) => {
    try {
      const scheduled_at = new Date(
        `${data.scheduled_date}T${data.scheduled_time}`,
      ).toISOString();
      await createAppointment.mutateAsync({
        patient_id: data.patient_id,
        provider_id: data.provider_id,
        scheduled_at,
        duration_minutes: data.duration_minutes,
        appointment_type: data.appointment_type,
        reason: data.reason || undefined,
      });
      toast.success("Appointment created successfully");
      onOpenChange(false);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to create appointment";
      toast.error(message);
    }
  };

  // Loading state for role determination
  if (isRoleLoading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[500px]">
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Schedule Appointment</DialogTitle>
          <DialogDescription>
            {roleInfo?.role === "patient"
              ? "Schedule an appointment for yourself."
              : "Create a new appointment for a patient."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Patient Selector - Role-based */}
          <div className="space-y-2">
            <Label htmlFor="patient">Patient *</Label>
            {/* Patient role: show fixed "You" */}
            {roleInfo?.role === "patient" ? (
              <Input value="You" disabled className="bg-muted" />
            ) : /* Has default patient ID: show read-only */
            defaultPatientId ? (
              <Input
                value={selectedPatientName || "Selected Patient"}
                disabled
              />
            ) : /* Proxy with single patient: show read-only */
            roleInfo?.role === "proxy" && patientOptions.length === 1 ? (
              <Input
                value={`${patientOptions[0].lastName}, ${patientOptions[0].firstName}`}
                disabled
                className="bg-muted"
              />
            ) : /* Show patient selector for staff/provider/admin or proxy with multiple */
            showPatientSelector ? (
              <Popover open={patientOpen} onOpenChange={setPatientOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={patientOpen}
                    className="w-full justify-between"
                  >
                    {selectedPatientName || "Select patient..."}
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-[400px] p-0">
                  <Command shouldFilter={false}>
                    {/* Only show search for non-proxy roles */}
                    {roleInfo?.role !== "proxy" && (
                      <CommandInput
                        placeholder="Search patients..."
                        value={patientSearch}
                        onValueChange={setPatientSearch}
                      />
                    )}
                    <CommandList>
                      {isPatientListLoading ? (
                        <div className="flex items-center justify-center py-6">
                          <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                      ) : (
                        <>
                          <CommandEmpty>No patients found.</CommandEmpty>
                          <CommandGroup>
                            {patientOptions.map((patient) => (
                              <CommandItem
                                key={patient.id}
                                value={patient.id}
                                onSelect={() => {
                                  setValue("patient_id", patient.id);
                                  setSelectedPatientName(
                                    `${patient.lastName}, ${patient.firstName}`,
                                  );
                                  setPatientOpen(false);
                                }}
                              >
                                <Check
                                  className={cn(
                                    "mr-2 h-4 w-4",
                                    watchPatientId === patient.id
                                      ? "opacity-100"
                                      : "opacity-0",
                                  )}
                                />
                                <div>
                                  <div>
                                    {patient.lastName}, {patient.firstName}
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    DOB:{" "}
                                    {format(
                                      new Date(patient.dob),
                                      "MM/dd/yyyy",
                                    )}
                                    {patient.mrn && ` • MRN: ${patient.mrn}`}
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
            ) : (
              /* Fallback - should not reach here normally */
              <Input value="No patients available" disabled />
            )}
            {errors.patient_id && (
              <p className="text-sm text-destructive">Patient is required</p>
            )}
          </div>

          {/* Provider Selector */}
          <div className="space-y-2">
            <Label htmlFor="provider">Provider *</Label>
            <Select onValueChange={(val) => setValue("provider_id", val)}>
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
                {...register("scheduled_date", { required: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="scheduled_time">Time *</Label>
              <Input
                type="time"
                {...register("scheduled_time", { required: true })}
              />
            </div>
          </div>

          {/* Duration and Type */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="duration">Duration</Label>
              <Select
                defaultValue="30"
                onValueChange={(val) =>
                  setValue("duration_minutes", parseInt(val, 10))
                }
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
                onValueChange={(val) => setValue("appointment_type", val)}
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
              {...register("reason")}
              placeholder="Brief description of the appointment reason"
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
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
