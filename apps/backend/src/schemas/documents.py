"""Document schemas for API request/response."""

from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Allowed MIME types for document uploads (HIPAA compliance - P1-007)
ALLOWED_FILE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",  # Some systems use this instead of image/jpeg
    "image/png",
    "image/gif",
    "application/msword",  # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.ms-excel",  # .xls
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "text/plain",
    "text/csv",
}

# Allowed file extensions (lowercase)
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".csv"}

# Maximum file size (50 MB for document uploads)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class DocumentUploadRequest(BaseModel):
    """Request to get a presigned upload URL."""

    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(default="application/pdf", max_length=100)
    file_size: int = Field(..., gt=0, le=52428800)  # Max 50MB (updated from 10MB for medical documents)
    document_type: str = Field(default="OTHER")
    description: str | None = None

    @field_validator("file_name")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """
        Validate and sanitize filename.

        Security checks (P1-007):
        - Reject path traversal attempts (../, .., /, \\)
        - Whitelist file extensions
        - Ensure filename is not empty after stripping
        """
        if not v or len(v.strip()) == 0:
            raise ValueError("Filename cannot be empty")

        # Security: Prevent path traversal attacks
        if any(dangerous in v for dangerous in ["../", "..", "/", "\\"]):
            raise ValueError("Invalid filename: path traversal not allowed")

        # Validate file extension
        ext = Path(v).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File extension '{ext}' not allowed. "
                f"Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        return v

    @field_validator("file_type")
    @classmethod
    def validate_file_type(cls, v: str) -> str:
        """
        Validate file type against allowed MIME types.

        Addresses P1-007: File type validation to prevent malicious uploads.
        """
        if v not in ALLOWED_FILE_TYPES:
            raise ValueError(
                f"File type '{v}' is not allowed. "
                f"Allowed types: PDF, JPEG, PNG, GIF, Word documents, Excel spreadsheets, and plain text."
            )
        return v

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validate file size is within acceptable limits."""
        if v > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum of {MAX_FILE_SIZE // (1024 * 1024)} MB")
        if v <= 0:
            raise ValueError("File size must be greater than 0")
        return v


class DocumentUploadResponse(BaseModel):
    """Response with presigned upload URL."""

    document_id: UUID
    upload_url: str
    upload_fields: dict
    s3_key: str


class DocumentConfirmRequest(BaseModel):
    """Request to confirm document upload completion."""

    pass  # Empty body, just confirms the upload


class DocumentRead(BaseModel):
    """Full document read model."""

    id: UUID
    organization_id: UUID
    patient_id: UUID
    uploaded_by_user_id: UUID
    file_name: str
    file_type: str
    file_size: int
    s3_key: str
    document_type: str
    description: str | None
    status: str
    uploaded_at: datetime | None
    created_at: datetime
    updated_at: datetime

    # Convenience fields
    uploaded_by_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentListItem(BaseModel):
    """Lightweight document for list views."""

    id: UUID
    file_name: str
    file_type: str
    file_size: int
    document_type: str
    status: str
    uploaded_at: datetime | None
    uploaded_by_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentDownloadResponse(BaseModel):
    """Response with presigned download URL."""

    document_id: UUID
    download_url: str
    expires_in: int = 3600  # seconds


class PaginatedDocuments(BaseModel):
    """Paginated list of documents."""

    items: list[DocumentListItem]
    total: int
    limit: int
    offset: int
