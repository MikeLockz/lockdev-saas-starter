"""Document schemas for API request/response."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentUploadRequest(BaseModel):
    """Request to get a presigned upload URL."""

    file_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(default="application/pdf", max_length=100)
    file_size: int = Field(..., gt=0, le=10485760)  # Max 10MB
    document_type: str = Field(default="OTHER")
    description: Optional[str] = None


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
    description: Optional[str]
    status: str
    uploaded_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Convenience fields
    uploaded_by_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentListItem(BaseModel):
    """Lightweight document for list views."""

    id: UUID
    file_name: str
    file_type: str
    file_size: int
    document_type: str
    status: str
    uploaded_at: Optional[datetime]
    uploaded_by_name: Optional[str] = None

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
