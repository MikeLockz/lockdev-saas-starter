import { createFileRoute } from "@tanstack/react-router";
import { z } from "zod";
import { TaskBoard } from "@/components/tasks/TaskBoard";

export const Route = createFileRoute("/_auth/tasks/")({
  component: TaskBoard,
  validateSearch: z.object({
    view: z.enum(["board", "list"]).optional(),
  }),
});
