import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CareTeamList } from "./CareTeamList";

const mockMembers = [
  {
    assignment_id: "a1",
    provider_id: "p1",
    role: "PRIMARY",
    assigned_at: "2023-01-01T00:00:00Z",
    provider_name: "Dr. House",
    provider_specialty: "Diagnostic",
    provider_npi: "123",
  },
  {
    assignment_id: "a2",
    provider_id: "p2",
    role: "SPECIALIST",
    assigned_at: "2023-02-01T00:00:00Z",
    provider_name: "Dr. Wilson",
    provider_specialty: "Oncology",
    provider_npi: "456",
  },
];

const mockRemoveMutate = vi.fn().mockResolvedValue({});

vi.mock("@/hooks/useCareTeam", () => ({
  useCareTeam: () => ({
    data: { members: mockMembers },
    isLoading: false,
  }),
  useRemoveFromCareTeam: () => ({
    mutateAsync: mockRemoveMutate,
  }),
}));

// Mock AlertDialog components
vi.mock("@/components/ui/alert-dialog", () => ({
  AlertDialog: ({ children, open }: any) =>
    open ? <div>{children}</div> : null,
  AlertDialogContent: ({ children }: any) => <div>{children}</div>,
  AlertDialogHeader: ({ children }: any) => <div>{children}</div>,
  AlertDialogFooter: ({ children }: any) => <div>{children}</div>,
  AlertDialogTitle: ({ children }: any) => <div>{children}</div>,
  AlertDialogDescription: ({ children }: any) => <div>{children}</div>,
  AlertDialogAction: ({ onClick, children }: any) => (
    <button type="button" onClick={onClick}>
      {children}
    </button>
  ),
  AlertDialogCancel: ({ onClick, children }: any) => (
    <button type="button" onClick={onClick}>
      {children}
    </button>
  ),
}));

// Mock the Assign Modal since it has its own logic
vi.mock("./CareTeamAssignModal", () => ({
  CareTeamAssignModal: ({ open }: { open: boolean }) =>
    open ? <div>Assign Modal Open</div> : null,
}));

describe("CareTeamList", () => {
  it("renders care team members correctly", () => {
    render(<CareTeamList patientId="pat1" />);

    expect(screen.getByText("Dr. House")).toBeInTheDocument();
    expect(screen.getByText("PRIMARY")).toBeInTheDocument();
    expect(screen.getByText("Dr. Wilson")).toBeInTheDocument();
    expect(screen.getByText("SPECIALIST")).toBeInTheDocument();
  });

  it("opens assign modal when add button is clicked", () => {
    render(<CareTeamList patientId="pat1" />);

    fireEvent.click(screen.getByText("Assign Member"));
    expect(screen.getByText("Assign Modal Open")).toBeInTheDocument();
  });

  it("prompts removal confirmation", async () => {
    render(<CareTeamList patientId="pat1" />);

    // Find rows and get the remove button from first data row
    const rows = screen.getAllByRole("row");
    // rows[0] is header. rows[1] is first data row.
    const firstRow = rows[1];
    const removeButton = within(firstRow).getByRole("button");

    fireEvent.click(removeButton);

    expect(screen.getByText("Remove from Care Team?")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Remove"));

    expect(mockRemoveMutate).toHaveBeenCalledWith({
      patientId: "pat1",
      assignmentId: "a1",
    });
  });
});
