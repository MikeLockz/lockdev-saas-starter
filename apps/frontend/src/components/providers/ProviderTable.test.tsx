import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProviderTable } from "./ProviderTable";

const mockProviders = [
  {
    id: "1",
    user_id: "u1",
    user_display_name: "Dr. House",
    user_email: "house@example.com",
    npi_number: "1234567890",
    specialty: "Diagnostic Medicine",
    is_active: true,
  },
  {
    id: "2",
    user_id: "u2",
    user_display_name: "Dr. Wilson",
    user_email: "wilson@example.com",
    npi_number: "0987654321",
    specialty: "Oncology",
    is_active: false,
  },
];

const mockDeleteMutate = vi.fn();

vi.mock("@/hooks/useProviders", () => ({
  useProviders: ({ specialty }: { specialty?: string }) => ({
    data: {
      items: specialty
        ? mockProviders.filter((p) =>
            p.specialty?.toLowerCase().includes(specialty.toLowerCase()),
          )
        : mockProviders,
      total: 2,
    },
    isLoading: false,
  }),
  useDeleteProvider: () => ({
    mutateAsync: mockDeleteMutate,
  }),
}));

// Mock Dialog/Alert components if needed?
// They are rendered by the component, so we should testing-library query them.
// But we might need to mock them if they are complex or if they are from libraries we struggle with in tests.
// Let's assume standard render works since I implemented them in codebase (except radix primitives which jsdom should handle).

describe("ProviderTable", () => {
  it("renders provider list correctly", () => {
    render(<ProviderTable />);

    expect(screen.getByText("Dr. House")).toBeInTheDocument();
    expect(screen.getByText("Diagnostic Medicine")).toBeInTheDocument();
    expect(screen.getByText("1234567890")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();

    expect(screen.getByText("Dr. Wilson")).toBeInTheDocument();
    expect(screen.getByText("Inactive")).toBeInTheDocument();
  });

  it("filters providers by specialty", () => {
    render(<ProviderTable />);

    const input = screen.getByPlaceholderText("Filter by specialty...");
    fireEvent.change(input, { target: { value: "Oncology" } });

    // Since our mock implements filtering logic:
    // Wait for re-render if hook update requires it (it usually does)
    // Check if Dr. House is gone
    expect(screen.queryByText("Dr. House")).not.toBeInTheDocument();
    expect(screen.getByText("Dr. Wilson")).toBeInTheDocument();
  });

  it("calls onCreate when add button is clicked", () => {
    const onCreate = vi.fn();
    render(<ProviderTable onCreate={onCreate} />);

    fireEvent.click(screen.getByText("Add Provider"));
    expect(onCreate).toHaveBeenCalled();
  });

  it("opens delete confirmation and deletes", async () => {
    render(<ProviderTable />);

    // Click delete on first row (Dr. House)
    const deleteButtons = screen
      .getAllByRole("button", { name: "" })
      .filter((b) => b.classList.contains("text-destructive"));
    fireEvent.click(deleteButtons[0]);

    // Expect Dialog
    expect(screen.getByText("Are you sure?")).toBeInTheDocument();

    // Confirm
    fireEvent.click(screen.getByText("Delete"));

    expect(mockDeleteMutate).toHaveBeenCalledWith("1");
  });
});
