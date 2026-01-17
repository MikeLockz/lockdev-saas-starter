from arq.connections import RedisSettings

from app.core.config import settings


async def health_check_task(ctx):
    """
    Proof of concept task.
    """
    print("Background task 'health_check_task' is running...")
    return "OK"


async def process_document_job(ctx, object_name: str):
    """
    Processes a document using AWS Textract.
    """
    print(f"Processing document: {object_name}")
    # 1. Fetch from S3
    # 2. Call Textract
    # 3. Save results to DB
    return {"status": "processed", "text": "Extracted text placeholder"}


async def startup(ctx):
    print("Background worker starting up...")


async def shutdown(ctx):
    print("Background worker shutting down...")


class WorkerSettings:
    """
    Settings for the arq worker.
    Run with: arq app.worker.WorkerSettings
    """

    functions = [health_check_task, process_document_job]
    redis_settings = RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    on_startup = startup
    on_shutdown = shutdown
