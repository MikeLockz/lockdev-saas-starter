import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/axios";
import { useOrgStore } from "@/store/org-store";

// Types
export interface Document {
  id: string;
  organization_id: string;
  patient_id: string;
  uploaded_by_user_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  s3_key: string;
  document_type: string;
  description: string | null;
  status: string;
  uploaded_at: string | null;
  created_at: string;
  updated_at: string;
  uploaded_by_name: string | null;
}

export interface DocumentListItem {
  id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  document_type: string;
  status: string;
  uploaded_at: string | null;
  uploaded_by_name: string | null;
}

export interface PaginatedDocuments {
  items: DocumentListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface DocumentUploadRequest {
  file_name: string;
  file_type: string;
  file_size: number;
  document_type?: string;
  description?: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  upload_url: string;
  upload_fields: Record<string, string>;
  s3_key: string;
}

export interface DocumentDownloadResponse {
  document_id: string;
  download_url: string;
  expires_in: number;
}

// Hooks
export function usePatientDocuments(
  patientId: string | undefined,
  documentType?: string,
) {
  const currentOrgId = useOrgStore((state) => state.currentOrgId);

  return useQuery<PaginatedDocuments>({
    queryKey: ["documents", currentOrgId, patientId, documentType],
    queryFn: async () => {
      if (!currentOrgId || !patientId)
        throw new Error("Missing org or patient");
      const params = new URLSearchParams();
      if (documentType) params.set("document_type", documentType);
      const response = await api.get(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/documents?${params}`,
      );
      return response.data;
    },
    enabled: !!currentOrgId && !!patientId,
  });
}

export function useUploadDocument(patientId: string) {
  const queryClient = useQueryClient();
  const currentOrgId = useOrgStore((state) => state.currentOrgId);

  return useMutation({
    mutationFn: async ({
      file,
      documentType,
      description,
    }: {
      file: File;
      documentType?: string;
      description?: string;
    }) => {
      if (!currentOrgId) throw new Error("No organization selected");

      // Step 1: Get presigned upload URL
      const uploadRequest: DocumentUploadRequest = {
        file_name: file.name,
        file_type: file.type || "application/octet-stream",
        file_size: file.size,
        document_type: documentType || "OTHER",
        description,
      };

      const urlResponse = await api.post<DocumentUploadResponse>(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/documents/upload-url`,
        uploadRequest,
      );

      const { document_id, upload_url, upload_fields } = urlResponse.data;

      // Step 2: Upload file directly to S3
      const formData = new FormData();
      Object.entries(upload_fields).forEach(([key, value]) => {
        formData.append(key, value);
      });
      formData.append("file", file);

      await fetch(upload_url, {
        method: "POST",
        body: formData,
      });

      // Step 3: Confirm upload
      const confirmResponse = await api.post<Document>(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/documents/${document_id}/confirm`,
      );

      return confirmResponse.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["documents", currentOrgId, patientId],
      });
    },
  });
}

export function useDownloadDocument(patientId: string) {
  const currentOrgId = useOrgStore((state) => state.currentOrgId);

  return useMutation({
    mutationFn: async (documentId: string) => {
      if (!currentOrgId) throw new Error("No organization selected");

      const response = await api.get<DocumentDownloadResponse>(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/documents/${documentId}/download-url`,
      );

      // Open in new tab
      window.open(response.data.download_url, "_blank");
      return response.data;
    },
  });
}

export function useDeleteDocument(patientId: string) {
  const queryClient = useQueryClient();
  const currentOrgId = useOrgStore((state) => state.currentOrgId);

  return useMutation({
    mutationFn: async (documentId: string) => {
      if (!currentOrgId) throw new Error("No organization selected");
      await api.delete(
        `/api/v1/organizations/${currentOrgId}/patients/${patientId}/documents/${documentId}`,
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["documents", currentOrgId, patientId],
      });
    },
  });
}
