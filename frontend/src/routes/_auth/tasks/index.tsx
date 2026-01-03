import { createFileRoute } from '@tanstack/react-router';
import { TaskBoard } from '@/components/tasks/TaskBoard';
import { z } from 'zod';

export const Route = createFileRoute('/_auth/tasks/')({
    component: TaskBoard,
    validateSearch: z.object({
        view: z.enum(['board', 'list']).optional(),
    }),
});
