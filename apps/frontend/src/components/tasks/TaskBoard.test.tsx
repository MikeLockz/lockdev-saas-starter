import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { usePatients } from "@/hooks/api/usePatients";
import { useStaff } from "@/hooks/api/useStaff";
import {
  useCreateTask,
  useDeleteTask,
  useTasks,
  useUpdateTask,
} from "@/hooks/api/useTasks";
import { TaskBoard } from "./TaskBoard";

// Mock the hooks
vi.mock("@/hooks/api/useTasks");
vi.mock("@/hooks/api/usePatients");
vi.mock("@/hooks/api/useStaff");

describe("TaskBoard", () => {
  const mockTasks = [
    {
      id: "1",
      title: "Task 1",
      description: "Description 1",
      status: "TODO",
      priority: "HIGH",
      assignee_name: "John Doe",
    },
    {
      id: "2",
      title: "Task 2",
      description: "Description 2",
      status: "IN_PROGRESS",
      priority: "MEDIUM",
      assignee_name: "Jane Doe",
    },
    {
      id: "3",
      title: "Task 3",
      description: "Description 3",
      status: "DONE",
      priority: "LOW",
      assignee_name: "Bob Smith",
    },
  ];

  const mockCreateTask = vi.fn();
  const mockUpdateTask = vi.fn();
  const mockDeleteTask = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useTasks as any).mockReturnValue({ data: mockTasks });
    (usePatients as any).mockReturnValue({ data: { items: [] } });
    (useStaff as any).mockReturnValue({ data: [] });
    (useCreateTask as any).mockReturnValue({ mutate: mockCreateTask });
    (useUpdateTask as any).mockReturnValue({ mutate: mockUpdateTask });
    (useDeleteTask as any).mockReturnValue({ mutate: mockDeleteTask });
  });

  it("renders the task board with columns", () => {
    render(<TaskBoard />);

    expect(screen.getByText("Task Board")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /to do/i })).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /in progress/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /done/i })).toBeInTheDocument();
  });

  it("displays tasks in correct columns", () => {
    render(<TaskBoard />);
    expect(screen.getByText("Task 1")).toBeInTheDocument();
    expect(screen.getByText("Task 2")).toBeInTheDocument();
    expect(screen.getByText("Task 3")).toBeInTheDocument();
  });

  it('opens the create task modal when clicking "New Task"', () => {
    render(<TaskBoard />);
    fireEvent.click(screen.getByText("New Task"));
    expect(screen.getByText("Create New Task")).toBeInTheDocument();
  });

  it("submits a new task", async () => {
    render(<TaskBoard />);
    fireEvent.click(screen.getByText("New Task"));

    const titleInput = screen.getByPlaceholderText("Task title");
    fireEvent.change(titleInput, { target: { value: "New Task Title" } });

    fireEvent.click(screen.getByText("Create Task"));

    await waitFor(() => {
      expect(mockCreateTask).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "New Task Title",
        }),
        expect.anything(),
      );
    });
  });
});
