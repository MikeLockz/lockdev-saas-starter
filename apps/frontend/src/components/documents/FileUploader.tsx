import { FileImage, FileText, Loader2, Upload, X } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useUploadDocument } from "@/hooks/api/usePatientDocuments";
import { cn } from "@/lib/utils";

interface FileUploaderProps {
  patientId: string;
  onUploadComplete?: () => void;
}

const DOCUMENT_TYPES = [
  { value: "LAB_RESULT", label: "Lab Result" },
  { value: "IMAGING", label: "Imaging" },
  { value: "CONSENT_FORM", label: "Consent Form" },
  { value: "REFERRAL", label: "Referral" },
  { value: "PRESCRIPTION", label: "Prescription" },
  { value: "OTHER", label: "Other" },
];

const ACCEPTED_TYPES = [
  "application/pdf",
  "image/png",
  "image/jpeg",
  "image/gif",
  "image/webp",
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export function FileUploader({
  patientId,
  onUploadComplete,
}: FileUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("OTHER");
  const [description, setDescription] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useUploadDocument(patientId);

  const validateFile = (file: File): boolean => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      toast.error("Invalid file type. Please upload PDF or images.");
      return false;
    }
    if (file.size > MAX_FILE_SIZE) {
      toast.error("File too large. Maximum size is 10MB.");
      return false;
    }
    return true;
  };

  const handleFileSelect = (file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
      setUploadProgress(0);
    }
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFileSelect(file);
    },
    [handleFileSelect],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploadProgress(10);
      await uploadMutation.mutateAsync({
        file: selectedFile,
        documentType,
        description: description || undefined,
      });
      setUploadProgress(100);
      toast.success("Document uploaded successfully");
      setSelectedFile(null);
      setDescription("");
      setDocumentType("OTHER");
      onUploadComplete?.();
    } catch (_error) {
      toast.error("Failed to upload document");
      setUploadProgress(0);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith("image/")) {
      return <FileImage className="h-8 w-8 text-blue-500" />;
    }
    return <FileText className="h-8 w-8 text-red-500" />;
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer",
          isDragging
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-primary/50",
          selectedFile && "border-green-500 bg-green-50",
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept={ACCEPTED_TYPES.join(",")}
          onChange={handleInputChange}
        />

        {selectedFile ? (
          <div className="flex items-center justify-center gap-4">
            {getFileIcon(selectedFile.type)}
            <div className="text-left">
              <p className="font-medium">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                clearSelection();
              }}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="h-10 w-10 mx-auto text-muted-foreground" />
            <p className="text-muted-foreground">
              Drag and drop a file, or click to browse
            </p>
            <p className="text-xs text-muted-foreground">
              PDF, PNG, JPEG • Max 10MB
            </p>
          </div>
        )}
      </div>

      {/* Options */}
      {selectedFile && (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label>Document Type</Label>
            <Select value={documentType} onValueChange={setDocumentType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DOCUMENT_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Description (optional)</Label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description..."
            />
          </div>
        </div>
      )}

      {/* Progress */}
      {uploadMutation.isPending && (
        <Progress value={uploadProgress} className="h-2" />
      )}

      {/* Upload Button */}
      {selectedFile && (
        <Button
          onClick={handleUpload}
          disabled={uploadMutation.isPending}
          className="w-full"
        >
          {uploadMutation.isPending ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4 mr-2" />
              Upload Document
            </>
          )}
        </Button>
      )}
    </div>
  );
}
