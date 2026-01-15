import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useCalls, useCreateCall, useUpdateCall } from "@/hooks/api/useCalls";
import { usePatients } from "@/hooks/api/usePatients";
import { CallCenterDashboard } from "./CallCenterDashboard";

// Mock the hooks
vi.mock("@/hooks/api/useCalls");
vi.mock("@/hooks/api/usePatients");

describe("CallCenterDashboard", () => {
  const mockCalls = [
    {
      id: "1",
      status: "IN_PROGRESS",
      direction: "INBOUND",
      phone_number: "+1234567890",
      created_at: new Date().toISOString(),
    },
    {
      id: "2",
      status: "QUEUED",
      direction: "INBOUND",
      phone_number: "+0987654321",
      created_at: new Date().toISOString(),
    },
    {
      id: "3",
      status: "COMPLETED",
      direction: "OUTBOUND",
      phone_number: "+1122334455",
      created_at: new Date().toISOString(),
      outcome: "RESOLVED",
    },
  ];

  const mockCreateCall = vi.fn();
  const mockUpdateCall = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Default implementation returns all calls
    // Default implementation returns all calls
    vi.mocked(useCalls).mockImplementation((filters: unknown) => {
      const f = filters as { status?: string } | undefined;
      if (f?.status === "QUEUED") {
        return { data: [mockCalls[1]] } as unknown as ReturnType<
          typeof useCalls
        >;
      }
      return { data: mockCalls } as unknown as ReturnType<typeof useCalls>;
    });
    vi.mocked(usePatients).mockReturnValue({
      data: { items: [] },
    } as unknown as ReturnType<typeof usePatients>);
    vi.mocked(useCreateCall).mockReturnValue({
      mutate: mockCreateCall,
    } as unknown as ReturnType<typeof useCreateCall>);
    vi.mocked(useUpdateCall).mockReturnValue({
      mutate: mockUpdateCall,
    } as unknown as ReturnType<typeof useUpdateCall>);
  });

  it("renders the dashboard with call queue, active calls, and history", () => {
    render(<CallCenterDashboard />);

    expect(screen.getByText("Call Center")).toBeInTheDocument();
    expect(screen.getByText("Call Queue")).toBeInTheDocument();
    expect(screen.getByText("Active Calls")).toBeInTheDocument();
    expect(screen.getByText("Recent History")).toBeInTheDocument();
  });

  it("displays active calls", () => {
    render(<CallCenterDashboard />);
    expect(screen.getByText("+1234567890")).toBeInTheDocument();
  });

  it("displays queued calls in the queue section", () => {
    render(<CallCenterDashboard />);
    // The queued phone number should be present
    expect(screen.getByText("+0987654321")).toBeInTheDocument();
  });

  it('opens the log call modal when clicking "Log Call"', () => {
    render(<CallCenterDashboard />);
    fireEvent.click(screen.getByText("Log Call"));
    expect(screen.getByText("Log New Call")).toBeInTheDocument();
  });

  it("submits a new call log", async () => {
    render(<CallCenterDashboard />);
    fireEvent.click(screen.getByText("Log Call"));

    const phoneInput = screen.getByPlaceholderText("+1234567890");
    fireEvent.change(phoneInput, { target: { value: "+5555555555" } });

    fireEvent.click(screen.getByText("Save Call"));

    await waitFor(() => {
      expect(mockCreateCall).toHaveBeenCalledWith(
        expect.objectContaining({
          phone_number: "+5555555555",
        }),
        expect.anything(),
      );
    });
  });
});
