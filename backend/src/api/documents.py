"""
Document API endpoints.

Provides endpoints for document upload and processing.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.documents import generate_upload_url
from src.worker import enqueue_task, get_job_result

router = APIRouter(prefix="/documents", tags=["documents"])


class UploadURLRequest(BaseModel):
    """Request model for upload URL generation."""

    filename: str
    content_type: str = "application/pdf"


class UploadURLResponse(BaseModel):
    """Response model for upload URL."""

    url: str
    fields: dict
    s3_key: str


class ProcessDocumentRequest(BaseModel):
    """Request model for document processing."""

    s3_key: str


class ProcessDocumentResponse(BaseModel):
    """Response model for document processing."""

    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    """Response model for job status."""

    job_id: str
    status: str
    result: dict | None = None


@router.post("/upload-url", response_model=UploadURLResponse)
async def create_upload_url(request: UploadURLRequest):
    """
    Generate presigned S3 URL for document upload.

    Args:
        request: Upload URL request with filename and content type

    Returns:
        Presigned POST URL with fields and S3 key

    Raises:
        HTTPException: If URL generation fails
    """
    try:
        result = await generate_upload_url(
            filename=request.filename,
            content_type=request.content_type,
        )
        return UploadURLResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/process", response_model=ProcessDocumentResponse)
async def process_document(request: ProcessDocumentRequest):
    """
    Trigger async document processing job.

    Args:
        request: Process request with S3 key

    Returns:
        Job ID for status polling

    Raises:
        HTTPException: If job enqueueing fails
    """
    try:
        job_id = await enqueue_task("process_document_task", request.s3_key)
        return ProcessDocumentResponse(job_id=job_id, status="enqueued")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {e}") from e


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of document processing job.

    Args:
        job_id: Job ID from process endpoint

    Returns:
        Job status and result if complete

    Raises:
        HTTPException: If job not found
    """
    try:
        result = await get_job_result(job_id)

        if result is None:
            return JobStatusResponse(job_id=job_id, status="pending", result=None)

        return JobStatusResponse(job_id=job_id, status="complete", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {e}") from e

