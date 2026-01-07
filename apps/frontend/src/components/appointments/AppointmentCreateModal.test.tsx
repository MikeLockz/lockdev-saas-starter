import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AppointmentCreateModal } from "./AppointmentCreateModal";

const mockPatients = [
  {
    id: "p-1",
    first_name: "John",
    last_name: "Doe",
    dob: "1990-01-15",
    medical_record_number: "MRN001",
    enrolled_at: null,
    status: "ACTIVE",
  },
  {
    id: "p-2",
    first_name: "Jane",
    last_name: "Smith",
    dob: "1985-05-20",
    medical_record_number: null,
    enrolled_at: null,
    status: "ACTIVE",
  },
];

const mockProviders = [
  {
    id: "prov-1",
    user_id: "u1",
    user_display_name: "Dr. Smith",
    user_email: "smith@example.com",
    npi_number: null,
    specialty: "Internal Medicine",
    is_active: true,
  },
  {
    id: "prov-2",
    user_id: "u2",
    user_display_name: "Dr. Jones",
    user_email: "jones@example.com",
    npi_number: null,
    specialty: "Cardiology",
    is_active: true,
  },
];

const mockCreateMutate = vi.fn();

vi.mock("@/hooks/api/useAppointments", () => ({
  useCreateAppointment: () => ({
    mutateAsync: mockCreateMutate,
    isPending: false,
  }),
}));

vi.mock("@/hooks/api/usePatients", () => ({
  usePatients: () => ({
    data: {
      items: mockPatients,
      total: 2,
    },
    isLoading: false,
  }),
}));

vi.mock("@/hooks/useProviders", () => ({
  useProviders: () => ({
    data: {
      items: mockProviders,
      total: 2,
    },
    isLoading: false,
  }),
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe("AppointmentCreateModal", () => {
  const onOpenChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders modal when open", () => {
    render(<AppointmentCreateModal open={true} onOpenChange={onOpenChange} />);

    expect(screen.getByText("Schedule Appointment")).toBeInTheDocument();
    expect(
      screen.getByText("Create a new appointment for a patient."),
    ).toBeInTheDocument();
  });

  it("does not render when closed", () => {
    render(<AppointmentCreateModal open={false} onOpenChange={onOpenChange} />);

    expect(screen.queryByText("Schedule Appointment")).not.toBeInTheDocument();
  });

  it("shows all required form fields", () => {
    render(<AppointmentCreateModal open={true} onOpenChange={onOpenChange} />);

    expect(screen.getByText("Patient *")).toBeInTheDocument();
    expect(screen.getByText("Provider *")).toBeInTheDocument();
    expect(screen.getByText("Date *")).toBeInTheDocument();
    expect(screen.getByText("Time *")).toBeInTheDocument();
    expect(screen.getByText("Duration")).toBeInTheDocument();
    expect(screen.getByText("Type")).toBeInTheDocument();
    expect(screen.getByText("Reason")).toBeInTheDocument();
  });

  it("shows patient and provider selectors", () => {
    render(<AppointmentCreateModal open={true} onOpenChange={onOpenChange} />);

    // Multiple comboboxes: patient selector and provider selector
    const comboboxes = screen.getAllByRole("combobox");
    expect(comboboxes.length).toBeGreaterThanOrEqual(2);
  });

  it("has schedule and cancel buttons", () => {
    render(<AppointmentCreateModal open={true} onOpenChange={onOpenChange} />);

    expect(
      screen.getByRole("button", { name: /schedule/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
  });

  it("calls onOpenChange when cancel is clicked", () => {
    render(<AppointmentCreateModal open={true} onOpenChange={onOpenChange} />);

    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("uses defaultPatientId when provided", () => {
    render(
      <AppointmentCreateModal
        open={true}
        onOpenChange={onOpenChange}
        defaultPatientId="p-1"
      />,
    );

    // When defaultPatientId is provided, input should be disabled
    expect(screen.getByDisplayValue("Selected Patient")).toBeInTheDocument();
  });
});
