"""Document API endpoints with organization and patient scoping.

Provides endpoints for secure document upload/download using S3 presigned URLs.
"""

from datetime import UTC, datetime
from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.documents import Document
from src.models.organizations import OrganizationMember
from src.models.profiles import Patient
from src.models.users import User
from src.schemas.documents import (
    DocumentDownloadResponse,
    DocumentListItem,
    DocumentRead,
    DocumentUploadRequest,
    DocumentUploadResponse,
    PaginatedDocuments,
)
from src.security.org_access import get_current_org_member

router = APIRouter()


def _generate_s3_key(org_id: UUID, patient_id: UUID, document_id: UUID, filename: str) -> str:
    """Generate S3 key following org/patient/doc/filename pattern."""
    return f"{org_id}/{patient_id}/{document_id}/{filename}"


async def _get_patient_or_404(db: AsyncSession, patient_id: UUID, org_id: UUID) -> Patient:
    """Get patient ensuring it belongs to organization."""
    result = await db.execute(
        select(Patient)
        .join(Patient.organizations)
        .where(Patient.id == patient_id)
        .where(Patient.organizations.any(organization_id=org_id))
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


async def _get_document_or_404(db: AsyncSession, document_id: UUID, org_id: UUID) -> Document:
    """Get document ensuring it belongs to organization."""
    result = await db.execute(
        select(Document).where(Document.id == document_id).where(Document.organization_id == org_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post(
    "/organizations/{org_id}/patients/{patient_id}/documents/upload-url",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_upload_url(
    org_id: UUID,
    patient_id: UUID,
    request: DocumentUploadRequest,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Generate presigned S3 URL for document upload."""
    # Verify patient exists in org
    await _get_patient_or_404(db, patient_id, org_id)

    # Create document record (PENDING status)
    document = Document(
        organization_id=org_id,
        patient_id=patient_id,
        uploaded_by_user_id=member.user_id,
        file_name=request.file_name,
        file_type=request.file_type,
        file_size=request.file_size,
        document_type=request.document_type,
        description=request.description,
        status="PENDING",
        s3_key="",  # Will be set after we have the ID
    )
    db.add(document)
    await db.flush()  # Get the ID

    # Generate S3 key
    s3_key = _generate_s3_key(org_id, patient_id, document.id, request.file_name)
    document.s3_key = s3_key

    await db.commit()
    await db.refresh(document)

    # Generate presigned POST URL
    if not settings.AWS_S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3 bucket not configured")

    try:
        s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
        presigned = s3_client.generate_presigned_post(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key,
            Fields={"Content-Type": request.file_type},
            Conditions=[
                {"Content-Type": request.file_type},
                ["content-length-range", 0, request.file_size + 1024],  # Allow small overhead
            ],
            ExpiresIn=900,  # 15 minutes
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate upload URL: {e}")

    return DocumentUploadResponse(
        document_id=document.id,
        upload_url=presigned["url"],
        upload_fields=presigned["fields"],
        s3_key=s3_key,
    )


@router.post(
    "/organizations/{org_id}/patients/{patient_id}/documents/{document_id}/confirm",
    response_model=DocumentRead,
)
async def confirm_upload(
    org_id: UUID,
    patient_id: UUID,
    document_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Confirm document upload completion."""
    document = await _get_document_or_404(db, document_id, org_id)

    if document.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status != "PENDING":
        raise HTTPException(status_code=400, detail="Document already confirmed")

    document.status = "UPLOADED"
    document.uploaded_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(document)

    # Get uploader name
    user_result = await db.execute(select(User).where(User.id == document.uploaded_by_user_id))
    uploader = user_result.scalar_one_or_none()

    return DocumentRead(
        **document.__dict__,
        uploaded_by_name=uploader.display_name if uploader else None,
    )


@router.get(
    "/organizations/{org_id}/patients/{patient_id}/documents",
    response_model=PaginatedDocuments,
)
async def list_documents(
    org_id: UUID,
    patient_id: UUID,
    document_type: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """List documents for a patient."""
    # Verify patient exists in org
    await _get_patient_or_404(db, patient_id, org_id)

    # Build query
    query = (
        select(Document)
        .where(Document.organization_id == org_id)
        .where(Document.patient_id == patient_id)
        .where(Document.status != "DELETED")
    )

    if document_type:
        query = query.where(Document.document_type == document_type)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch with pagination
    query = query.order_by(Document.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    documents = result.scalars().all()

    # Get uploader names
    user_ids = [d.uploaded_by_user_id for d in documents]
    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {u.id: u.display_name for u in users_result.scalars().all()}

    items = [
        DocumentListItem(
            id=doc.id,
            file_name=doc.file_name,
            file_type=doc.file_type,
            file_size=doc.file_size,
            document_type=doc.document_type,
            status=doc.status,
            uploaded_at=doc.uploaded_at,
            uploaded_by_name=users.get(doc.uploaded_by_user_id),
        )
        for doc in documents
    ]

    return PaginatedDocuments(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/organizations/{org_id}/patients/{patient_id}/documents/{document_id}/download-url",
    response_model=DocumentDownloadResponse,
)
async def get_download_url(
    org_id: UUID,
    patient_id: UUID,
    document_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Generate presigned S3 URL for document download."""
    document = await _get_document_or_404(db, document_id, org_id)

    if document.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status != "UPLOADED":
        raise HTTPException(status_code=400, detail="Document not available for download")

    if not settings.AWS_S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3 bucket not configured")

    try:
        s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
        download_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_S3_BUCKET, "Key": document.s3_key},
            ExpiresIn=3600,  # 1 hour
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {e}")

    return DocumentDownloadResponse(
        document_id=document.id,
        download_url=download_url,
        expires_in=3600,
    )


@router.delete(
    "/organizations/{org_id}/patients/{patient_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    org_id: UUID,
    patient_id: UUID,
    document_id: UUID,
    member: OrganizationMember = Depends(get_current_org_member),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a document."""
    document = await _get_document_or_404(db, document_id, org_id)

    if document.patient_id != patient_id:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = "DELETED"
    await db.commit()

    # Optionally delete from S3 (commented out for soft delete)
    # try:
    #     s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
    #     s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=document.s3_key)
    # except ClientError:
    #     pass  # Log but don't fail
