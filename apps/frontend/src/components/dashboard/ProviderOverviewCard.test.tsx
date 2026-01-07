import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProviderOverviewCard } from "@/components/dashboard/ProviderOverviewCard";

// Mock the hooks
vi.mock("@/hooks/api/useDashboardStats", () => ({
  useProviderTodaysAppointments: vi.fn(),
  useProviderPendingTasks: vi.fn(),
}));

import {
  useProviderPendingTasks,
  useProviderTodaysAppointments,
} from "@/hooks/api/useDashboardStats";

const mockUseProviderTodaysAppointments =
  useProviderTodaysAppointments as ReturnType<typeof vi.fn>;
const mockUseProviderPendingTasks = useProviderPendingTasks as ReturnType<
  typeof vi.fn
>;

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("ProviderOverviewCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state", () => {
    mockUseProviderTodaysAppointments.mockReturnValue({
      data: undefined,
      isLoading: true,
    });
    mockUseProviderPendingTasks.mockReturnValue({
      data: undefined,
      isLoading: true,
    });

    render(<ProviderOverviewCard providerId="provider-1" userId="user-1" />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText("Today's Schedule")).toBeInTheDocument();
    expect(
      screen.getByText("Loading your appointments and tasks..."),
    ).toBeInTheDocument();
  });

  it("renders appointments and tasks", () => {
    const mockAppointments = [
      {
        id: "appt-1",
        patient_id: "patient-1",
        scheduled_at: new Date().toISOString(),
        duration_minutes: 30,
        appointment_type: "FOLLOW_UP",
        reason: "Checkup",
        status: "SCHEDULED",
        patient_name: "John Doe",
      },
      {
        id: "appt-2",
        patient_id: "patient-2",
        scheduled_at: new Date(Date.now() + 3600000).toISOString(),
        duration_minutes: 30,
        appointment_type: "INITIAL",
        reason: "New patient",
        status: "CONFIRMED",
        patient_name: "Jane Smith",
      },
    ];

    const mockTasks = [
      {
        id: "task-1",
        title: "Review labs",
        status: "TODO",
        priority: "URGENT",
        due_date: null,
      },
      {
        id: "task-2",
        title: "Sign discharge",
        status: "TODO",
        priority: "HIGH",
        due_date: null,
      },
    ];

    mockUseProviderTodaysAppointments.mockReturnValue({
      data: mockAppointments,
      isLoading: false,
    });
    mockUseProviderPendingTasks.mockReturnValue({
      data: mockTasks,
      isLoading: false,
    });

    render(<ProviderOverviewCard providerId="provider-1" userId="user-1" />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText("Today's Schedule")).toBeInTheDocument();
    expect(
      screen.getByText("2 appointments · 2 pending tasks"),
    ).toBeInTheDocument();
    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("2 urgent")).toBeInTheDocument();
    expect(screen.getByText("Review labs")).toBeInTheDocument();
    expect(screen.getByText("Sign discharge")).toBeInTheDocument();
  });

  it("renders empty state when no appointments", () => {
    mockUseProviderTodaysAppointments.mockReturnValue({
      data: [],
      isLoading: false,
    });
    mockUseProviderPendingTasks.mockReturnValue({
      data: [],
      isLoading: false,
    });

    render(<ProviderOverviewCard providerId="provider-1" userId="user-1" />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText("Today's Schedule")).toBeInTheDocument();
    expect(
      screen.getByText("0 appointments · 0 pending tasks"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No appointments scheduled for today"),
    ).toBeInTheDocument();
  });
});
