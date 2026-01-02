"""
ARQ Background Worker Configuration

This module configures the ARQ worker for processing background tasks.
ARQ uses Redis as a message broker and provides async task execution.

Usage:
    # Start the worker
    arq src.worker.WorkerSettings

    # Or with uvicorn/honcho in development
    honcho start -f Procfile.dev
"""
import asyncio
import logging
from typing import Any

from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.logging import configure_logging

logger = logging.getLogger(__name__)


# =============================================================================
# Background Tasks
# =============================================================================

async def health_check_task(ctx: dict[str, Any]) -> str:
    """
    Health check task to verify worker is functioning.
    
    This is a proof-of-concept task that demonstrates:
    - Task execution
    - Context access
    - Logging
    - Return values
    
    Args:
        ctx: ARQ context dictionary containing redis pool, job_id, etc.
    
    Returns:
        Status message
    """
    job_id = ctx.get("job_id", "unknown")
    logger.info("Health check task started", extra={"job_id": job_id})
    
    # Simulate some work
    await asyncio.sleep(1)
    
    logger.info("Health check task completed", extra={"job_id": job_id})
    return f"Health check passed for job {job_id}"


async def send_email_task(ctx: dict[str, Any], to: str, subject: str, body: str) -> dict[str, Any]:
    """
    Send email via AWS SES (example task).
    
    Args:
        ctx: ARQ context
        to: Recipient email address
        subject: Email subject
        body: Email body
    
    Returns:
        Result dictionary with status
    """
    job_id = ctx.get("job_id", "unknown")
    logger.info(f"Sending email to {to}", extra={"job_id": job_id, "subject": subject})
    
    # TODO: Implement actual SES integration
    # For now, just simulate sending
    await asyncio.sleep(0.5)
    
    logger.info("Email sent successfully", extra={"job_id": job_id, "to": to})
    return {"status": "sent", "to": to, "subject": subject, "body_length": len(body), "job_id": job_id}


async def process_document_task(ctx: dict[str, Any], s3_key: str) -> dict[str, Any]:
    """
    Process uploaded document from S3 using Textract.
    
    Args:
        ctx: ARQ context
        s3_key: S3 object key of the uploaded document
    
    Returns:
        Processing result with extracted text
    """
    job_id = ctx.get("job_id", "unknown")
    logger.info(f"Processing document from S3: {s3_key}", extra={"job_id": job_id})
    
    try:
        # Import here to avoid circular dependencies
        from src.services.documents import download_from_s3, extract_text_from_document
        
        # Download file from S3
        logger.info("Downloading document from S3", extra={"job_id": job_id, "s3_key": s3_key})
        file_bytes = await download_from_s3(s3_key)
        
        # Extract text using Textract
        logger.info("Extracting text with Textract", extra={"job_id": job_id, "file_size": len(file_bytes)})
        extracted_text = await extract_text_from_document(file_bytes)
        
        logger.info(
            "Document processed successfully",
            extra={
                "job_id": job_id,
                "s3_key": s3_key,
                "text_length": len(extracted_text),
            },
        )
        
        return {
            "status": "processed",
            "s3_key": s3_key,
            "extracted_text": extracted_text,
            "text_length": len(extracted_text),
            "job_id": job_id,
        }
    
    except Exception as e:
        logger.error(
            "Document processing failed",
            extra={
                "job_id": job_id,
                "s3_key": s3_key,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        return {
            "status": "failed",
            "s3_key": s3_key,
            "error": str(e),
            "job_id": job_id,
        }


# =============================================================================
# Worker Lifecycle Hooks
# =============================================================================

async def startup(ctx: dict[str, Any]) -> None:
    """
    Worker startup hook.
    
    Initializes:
    - Logging configuration
    - Database connection pool
    - Any other shared resources
    
    Args:
        ctx: ARQ context (will be passed to all tasks)
    """
    # Configure structured logging
    configure_logging()
    logger.info("ARQ worker starting up")
    
    # Create database engine for worker tasks
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    
    # Create session factory
    async_session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Store in context for task access
    ctx["db_engine"] = engine
    ctx["db_session_factory"] = async_session_factory
    
    logger.info("ARQ worker startup complete")


async def shutdown(ctx: dict[str, Any]) -> None:
    """
    Worker shutdown hook.
    
    Cleans up:
    - Database connections
    - Any other resources
    
    Args:
        ctx: ARQ context
    """
    logger.info("ARQ worker shutting down")
    
    # Close database engine
    if "db_engine" in ctx:
        await ctx["db_engine"].dispose()
        logger.info("Database connections closed")
    
    logger.info("ARQ worker shutdown complete")


# =============================================================================
# Worker Settings
# =============================================================================

class WorkerSettings:
    """
    ARQ Worker configuration.
    
    See: https://arq-docs.helpmanual.io/
    """
    
    # Redis connection settings
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_DB,
    )
    
    # List of functions to register as tasks
    functions = [
        health_check_task,
        send_email_task,
        process_document_task,
    ]
    
    # Lifecycle hooks
    on_startup = startup
    on_shutdown = shutdown
    
    # Worker configuration
    max_jobs = 10  # Maximum concurrent jobs
    job_timeout = 300  # 5 minutes default timeout
    keep_result = 3600  # Keep results for 1 hour
    
    # Retry configuration
    max_tries = 3  # Retry failed jobs up to 3 times
    
    # Logging
    log_results = True
    
    # Health check interval (seconds)
    health_check_interval = 60


# =============================================================================
# Helper Functions for Enqueueing Tasks
# =============================================================================

async def enqueue_task(function_name: str, *args, **kwargs) -> str:
    """
    Helper function to enqueue a task from the API.
    
    Usage:
        job_id = await enqueue_task("health_check_task")
        job_id = await enqueue_task("send_email_task", "user@example.com", "Subject", "Body")
    
    Args:
        function_name: Name of the task function
        *args: Positional arguments for the task
        **kwargs: Keyword arguments for the task
    
    Returns:
        Job ID
    """
    redis = await create_pool(WorkerSettings.redis_settings)
    try:
        job = await redis.enqueue_job(function_name, *args, **kwargs)
        logger.info(f"Enqueued task {function_name}", extra={"job_id": job.job_id})
        return job.job_id
    finally:
        await redis.close()


async def get_job_result(job_id: str) -> Any:
    """
    Get the result of a completed job.
    
    Args:
        job_id: Job ID returned from enqueue_task
    
    Returns:
        Job result or None if not found/not complete
    """
    redis = await create_pool(WorkerSettings.redis_settings)
    try:
        job = await redis.get_job_result(job_id)
        return job
    finally:
        await redis.close()
