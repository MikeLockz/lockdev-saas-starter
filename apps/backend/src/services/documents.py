"""
Document Service using AWS S3 and Textract.

This module provides document upload and processing capabilities with
S3 presigned URLs and Textract text extraction.

Required Environment Variables:
    AWS_S3_BUCKET: S3 bucket name for document storage
    AWS_REGION: AWS region
    AWS_ACCESS_KEY_ID: AWS credentials (via boto3 default chain)
    AWS_SECRET_ACCESS_KEY: AWS credentials (via boto3 default chain)

Required AWS Permissions:
    - s3:PutObject (for presigned URLs)
    - s3:GetObject (for downloads)
    - textract:DetectDocumentText
"""

import boto3
import structlog
from botocore.exceptions import ClientError

from src.config import settings

logger = structlog.get_logger(__name__)


async def generate_upload_url(
    filename: str,
    content_type: str = "application/pdf",
    expiration: int = 900,  # 15 minutes
) -> dict:
    """
    Generate S3 presigned POST URL for file upload.

    Args:
        filename: Original filename
        content_type: MIME type of the file
        expiration: URL expiration time in seconds (default: 15 minutes)

    Returns:
        dict with url, fields, and s3_key

    Raises:
        ValueError: If filename is empty or bucket not configured
        RuntimeError: If AWS API call fails

    Security:
        - URLs expire after specified time
        - Content-type is enforced
        - File size limit enforced (10MB)
    """
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")

    if not settings.AWS_S3_BUCKET:
        raise ValueError("AWS_S3_BUCKET not configured")

    # Generate unique S3 key
    import uuid
    from datetime import datetime

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    s3_key = f"uploads/{timestamp}_{unique_id}_{filename}"

    logger.info(
        "generate_upload_url_requested",
        filename=filename,
        content_type=content_type,
        s3_key=s3_key,
    )

    try:
        s3_client = boto3.client("s3", region_name=settings.AWS_REGION)

        # Generate presigned POST
        response = s3_client.generate_presigned_post(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 0, 10485760],  # 10MB max
            ],
            ExpiresIn=expiration,
        )

        logger.info(
            "generate_upload_url_success",
            s3_key=s3_key,
            expiration=expiration,
        )

        return {
            "url": response["url"],
            "fields": response["fields"],
            "s3_key": s3_key,
        }

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(
            "generate_upload_url_failed",
            error_code=error_code,
            error_message=error_message,
        )

        raise RuntimeError(f"Failed to generate upload URL: {error_code} - {error_message}") from e
    except Exception as e:
        logger.error(
            "generate_upload_url_unexpected_error",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise RuntimeError(f"Upload URL generation error: {e}") from e


async def download_from_s3(s3_key: str) -> bytes:
    """
    Download file from S3.

    Args:
        s3_key: S3 object key

    Returns:
        File bytes

    Raises:
        ValueError: If s3_key is empty or bucket not configured
        RuntimeError: If download fails
    """
    if not s3_key or not s3_key.strip():
        raise ValueError("S3 key cannot be empty")

    if not settings.AWS_S3_BUCKET:
        raise ValueError("AWS_S3_BUCKET not configured")

    logger.info("download_from_s3_requested", s3_key=s3_key)

    try:
        s3_client = boto3.client("s3", region_name=settings.AWS_REGION)

        response = s3_client.get_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key,
        )

        file_bytes = response["Body"].read()
        file_size = len(file_bytes)

        logger.info(
            "download_from_s3_success",
            s3_key=s3_key,
            file_size=file_size,
        )

        return file_bytes

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(
            "download_from_s3_failed",
            s3_key=s3_key,
            error_code=error_code,
            error_message=error_message,
        )

        raise RuntimeError(f"S3 download failed: {error_code} - {error_message}") from e
    except Exception as e:
        logger.error(
            "download_from_s3_unexpected_error",
            s3_key=s3_key,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise RuntimeError(f"S3 download error: {e}") from e


async def extract_text_from_document(file_bytes: bytes) -> str:
    """
    Extract text from document using AWS Textract.

    Args:
        file_bytes: Document file bytes (PDF, PNG, JPEG, TIFF)

    Returns:
        Extracted text

    Raises:
        ValueError: If file_bytes is empty
        RuntimeError: If Textract API call fails

    Note:
        Uses synchronous detect_document_text API.
        For large multi-page documents, consider using async API.
    """
    if not file_bytes:
        raise ValueError("File bytes cannot be empty")

    if len(file_bytes) > 5242880:  # 5MB limit for synchronous API
        raise ValueError("File too large for synchronous processing (max 5MB)")

    logger.info(
        "extract_text_requested",
        file_size=len(file_bytes),
    )

    try:
        textract_client = boto3.client("textract", region_name=settings.AWS_REGION)

        response = textract_client.detect_document_text(Document={"Bytes": file_bytes})

        # Extract all text blocks
        text_blocks = []
        for block in response.get("Blocks", []):
            if block["BlockType"] == "LINE":
                text_blocks.append(block.get("Text", ""))

        extracted_text = "\n".join(text_blocks)

        logger.info(
            "extract_text_success",
            file_size=len(file_bytes),
            text_length=len(extracted_text),
            num_blocks=len(text_blocks),
        )

        return extracted_text

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(
            "extract_text_failed",
            error_code=error_code,
            error_message=error_message,
        )

        raise RuntimeError(f"Textract failed: {error_code} - {error_message}") from e
    except Exception as e:
        logger.error(
            "extract_text_unexpected_error",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise RuntimeError(f"Text extraction error: {e}") from e
