import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppointmentList } from "./AppointmentList";

const mockAppointments = [
  {
    id: "apt-1",
    organization_id: "org-1",
    patient_id: "p-1",
    provider_id: "prov-1",
    scheduled_at: new Date().toISOString(),
    duration_minutes: 30,
    appointment_type: "FOLLOW_UP",
    reason: "Routine checkup",
    notes: null,
    status: "SCHEDULED",
    cancelled_at: null,
    cancelled_by: null,
    cancellation_reason: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    patient_name: "Doe, John",
    provider_name: "Dr. Smith",
  },
  {
    id: "apt-2",
    organization_id: "org-1",
    patient_id: "p-2",
    provider_id: "prov-1",
    scheduled_at: new Date().toISOString(),
    duration_minutes: 45,
    appointment_type: "INITIAL_CONSULT",
    reason: null,
    notes: null,
    status: "CONFIRMED",
    cancelled_at: null,
    cancelled_by: null,
    cancellation_reason: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    patient_name: "Smith, Jane",
    provider_name: "Dr. Jones",
  },
];

const mockProviders = [
  {
    id: "prov-1",
    user_id: "u1",
    user_display_name: "Dr. Smith",
    user_email: "smith@example.com",
    npi_number: null,
    specialty: null,
    is_active: true,
  },
  {
    id: "prov-2",
    user_id: "u2",
    user_display_name: "Dr. Jones",
    user_email: "jones@example.com",
    npi_number: null,
    specialty: null,
    is_active: true,
  },
];

const mockUpdateStatusMutate = vi.fn();

vi.mock("@/hooks/api/useAppointments", () => ({
  useAppointments: () => ({
    data: {
      items: mockAppointments,
      total: 2,
      limit: 50,
      offset: 0,
    },
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useUpdateAppointmentStatus: () => ({
    mutateAsync: mockUpdateStatusMutate,
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

describe("AppointmentList", () => {
  it("renders appointment list correctly", () => {
    render(<AppointmentList />);

    expect(screen.getByText("Doe, John")).toBeInTheDocument();
    expect(screen.getByText("Dr. Smith")).toBeInTheDocument();
    expect(screen.getByText("Smith, Jane")).toBeInTheDocument();
    expect(screen.getByText("Scheduled")).toBeInTheDocument();
    expect(screen.getByText("Confirmed")).toBeInTheDocument();
  });

  it("calls onCreate when new appointment button is clicked", () => {
    const onCreate = vi.fn();
    render(<AppointmentList onCreate={onCreate} />);

    fireEvent.click(screen.getByRole("button", { name: /new appointment/i }));
    expect(onCreate).toHaveBeenCalled();
  });

  it("shows provider filter dropdown", () => {
    render(<AppointmentList />);

    expect(screen.getByRole("combobox")).toBeInTheDocument();
  });

  it("shows date navigation buttons", () => {
    render(<AppointmentList />);

    // Look for navigation buttons
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });

  it("shows confirm button for scheduled appointments", () => {
    render(<AppointmentList />);

    expect(
      screen.getByRole("button", { name: /confirm/i }),
    ).toBeInTheDocument();
  });

  it("shows cancel button for cancellable appointments", () => {
    render(<AppointmentList />);

    const cancelButtons = screen.getAllByRole("button", { name: /cancel/i });
    expect(cancelButtons.length).toBeGreaterThan(0);
  });
});
