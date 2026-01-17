import datetime

import structlog
from arq import cron
from arq.connections import RedisSettings
from sqlalchemy import delete

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.audit import AuditLog
from app.models.session import UserSession

logger = structlog.get_logger(__name__)


async def health_check_task(ctx):
    """
    Proof of concept task.
    """
    return "OK"


async def process_document_job(ctx, object_name: str):
    """
    Processes a document using AWS Textract.
    """
    # 1. Fetch from S3
    # 2. Call Textract
    # 3. Save results to DB
    return {"status": "processed", "text": "Extracted text placeholder"}


async def cleanup_expired_sessions(ctx):
    """
    [SEC-012] Delete expired user sessions.
    """
    async with AsyncSessionLocal() as session:
        now = datetime.datetime.now(datetime.UTC)
        stmt = delete(UserSession).where(UserSession.expires_at < now)
        result = await session.execute(stmt)
        await session.commit()
        count = result.rowcount
        logger.info("cleanup_expired_sessions", count=count)
        return f"Cleaned up {count} expired sessions"


async def enforce_data_retention(ctx):
    """
    [COMP-006] Delete audit logs older than the retention period (7 years).
    """
    retention_years = 7
    async with AsyncSessionLocal() as session:
        cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
            days=retention_years * 365
        )
        stmt = delete(AuditLog).where(AuditLog.created_at < cutoff)
        result = await session.execute(stmt)
        await session.commit()
        count = result.rowcount
        logger.info("enforce_data_retention", count=count)
        return f"Cleaned up {count} aged audit logs"


async def startup(ctx):
    logger.info("Worker starting up")


async def shutdown(ctx):
    logger.info("Worker shutting down")


class WorkerSettings:
    """
    Settings for the arq worker.
    Run with: arq app.worker.WorkerSettings
    """

    functions = [
        health_check_task,
        process_document_job,
        cleanup_expired_sessions,
        enforce_data_retention,
    ]
    cron_jobs = [
        cron(cleanup_expired_sessions, hour=0, minute=0),
        cron(enforce_data_retention, day=1, hour=1, minute=0),
    ]
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    on_startup = startup
    on_shutdown = shutdown
