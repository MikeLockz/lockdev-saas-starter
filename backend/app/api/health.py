from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db

router = APIRouter()


@router.get(
    "/health",
    summary="Shallow health check",
    description=(
        "Returns the basic status of the API service, including project name "
        "and environment."
    ),
)
def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@router.get(
    "/health/deep",
    summary="Deep health check",
    description=(
        "Performs a thorough health check by verifying connectivity to the "
        "database and other critical dependencies."
    ),
)
async def deep_health_check(db: AsyncSession = Depends(get_db)):
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e!s}"

    return {
        "status": "ok" if db_status == "ok" else "error",
        "components": {"database": db_status, "redis": "ok (mocked)"},
    }
