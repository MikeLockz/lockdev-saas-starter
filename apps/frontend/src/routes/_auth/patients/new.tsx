import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { ArrowLeft, Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { type PatientCreate, useCreatePatient } from "@/hooks/api/usePatients";

export const Route = createFileRoute("/_auth/patients/new")({
  component: NewPatientPage,
});

interface PatientFormData {
  first_name: string;
  last_name: string;
  dob: string;
  legal_sex: string;
  medical_record_number: string;
}

function NewPatientPage() {
  const navigate = useNavigate();
  const createPatientMutation = useCreatePatient();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<PatientFormData>({
    defaultValues: {
      first_name: "",
      last_name: "",
      dob: "",
      legal_sex: "",
      medical_record_number: "",
    },
  });

  const onSubmit = async (data: PatientFormData) => {
    try {
      const payload: PatientCreate = {
        first_name: data.first_name,
        last_name: data.last_name,
        dob: data.dob,
        legal_sex: data.legal_sex || undefined,
        medical_record_number: data.medical_record_number || undefined,
      };

      const patient = await createPatientMutation.mutateAsync(payload);
      toast.success("Patient created successfully");
      navigate({ to: `/patients/${patient.id}` });
    } catch (error) {
      toast.error("Failed to create patient");
      console.error("Create patient error:", error);
    }
  };

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
          <h1 className="text-lg font-semibold">New Patient</h1>
        </div>
      </Header>
      <Main>
        <form onSubmit={handleSubmit(onSubmit)} className="max-w-2xl space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Patient Information</CardTitle>
              <CardDescription>
                Enter the patient's basic information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name *</Label>
                  <Input
                    id="first_name"
                    {...register("first_name", {
                      required: "First name is required",
                    })}
                    placeholder="John"
                  />
                  {errors.first_name && (
                    <p className="text-sm text-destructive">
                      {errors.first_name.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name *</Label>
                  <Input
                    id="last_name"
                    {...register("last_name", {
                      required: "Last name is required",
                    })}
                    placeholder="Doe"
                  />
                  {errors.last_name && (
                    <p className="text-sm text-destructive">
                      {errors.last_name.message}
                    </p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="dob">Date of Birth *</Label>
                  <Input
                    id="dob"
                    type="date"
                    {...register("dob", {
                      required: "Date of birth is required",
                    })}
                  />
                  {errors.dob && (
                    <p className="text-sm text-destructive">
                      {errors.dob.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="legal_sex">Legal Sex</Label>
                  <Select
                    value={watch("legal_sex")}
                    onValueChange={(value: string) =>
                      setValue("legal_sex", value)
                    }
                  >
                    <SelectTrigger id="legal_sex">
                      <SelectValue placeholder="Select..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Male">Male</SelectItem>
                      <SelectItem value="Female">Female</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="medical_record_number">
                  Medical Record Number (MRN)
                </Label>
                <Input
                  id="medical_record_number"
                  {...register("medical_record_number")}
                  placeholder="Optional"
                  className="font-mono"
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate({ to: "/patients" })}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createPatientMutation.isPending}>
              {createPatientMutation.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Create Patient
            </Button>
          </div>
        </form>
      </Main>
    </>
  );
}
