from arq.connections import RedisSettings

from app.core.config import settings


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


async def startup(ctx):
    pass


async def shutdown(ctx):
    pass


class WorkerSettings:
    """
    Settings for the arq worker.
    Run with: arq app.worker.WorkerSettings
    """

    functions = [health_check_task, process_document_job]
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    on_startup = startup
    on_shutdown = shutdown
