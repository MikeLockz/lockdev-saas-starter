import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";

// Types
export interface Thread {
    id: string;
    organization_id: string;
    subject: string;
    created_at: string;
    updated_at: string;
    last_message?: Message;
    messages?: Message[];
    unread_count: number;
    participants: Participant[];
}

export interface Message {
    id: string;
    thread_id: string;
    sender_id?: string;
    sender_name?: string;
    body: string;
    created_at: string;
}

export interface Participant {
    user_id: string;
    user_name?: string;
    joined_at: string;
    last_read_at?: string;
}

export interface ThreadListResponse {
    items: Thread[];
    total: number;
    page: number;
    size: number;
}

export interface CreateThreadData {
    organization_id: string;
    subject: string;
    initial_message: string;
    participant_ids: string[];
    patient_id?: string;
}

export interface SendMessageData {
    body: string;
}

// Hooks

export const useThreads = (page = 1, size = 20) => {
    return useQuery({
        queryKey: ["threads", page, size],
        queryFn: async () => {
            const params = new URLSearchParams({
                page: page.toString(),
                size: size.toString(),
            });
            const { data } = await api.get<ThreadListResponse>(
                `/users/me/threads?${params.toString()}`
            );
            return data;
        },
    });
};

export const useThread = (threadId: string) => {
    return useQuery({
        queryKey: ["threads", threadId],
        queryFn: async () => {
            const { data } = await api.get<Thread>(`/users/me/threads/${threadId}`);
            return data;
        },
        enabled: !!threadId,
    });
};

export const useCreateThread = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (data: CreateThreadData) => {
            const response = await api.post<Thread>("/users/me/threads", data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["threads"] });
        },
    });
};

export const useSendMessage = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({
            threadId,
            data,
        }: {
            threadId: string;
            data: SendMessageData;
        }) => {
            const response = await api.post<Message>(
                `/users/me/threads/${threadId}/messages`,
                data
            );
            return response.data;
        },
        onSuccess: (_, { threadId }) => {
            queryClient.invalidateQueries({ queryKey: ["threads", threadId] });
            queryClient.invalidateQueries({ queryKey: ["threads"] }); // Update list preview
        },
    });
};

export const useMarkThreadRead = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (threadId: string) => {
            await api.post(`/users/me/threads/${threadId}/read`);
        },
        onSuccess: (_, threadId) => {
            queryClient.invalidateQueries({ queryKey: ["threads", threadId] });
            queryClient.invalidateQueries({ queryKey: ["threads"] });
        },
    });
};
