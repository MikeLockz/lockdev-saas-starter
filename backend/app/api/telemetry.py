import structlog
from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.telemetry import TelemetryBatch, TelemetryEvent

router = APIRouter()
logger = structlog.get_logger("analytics")


@router.post("")
async def track_event(
    data: TelemetryEvent, current_user: User = Depends(get_current_user)
):
    """
    Records a single behavioral event.
    """
    logger.info(
        "ANALYTICS_EVENT",
        user_id=current_user.id,
        event=data.event,
        properties=data.properties,
    )
    return {"status": "recorded"}


@router.post("/batch")
async def track_events_batch(
    data: TelemetryBatch, current_user: User = Depends(get_current_user)
):
    """
    Records a batch of behavioral events.
    """
    for event in data.events:
        logger.info(
            "ANALYTICS_EVENT",
            user_id=current_user.id,
            event=event.event,
            properties=event.properties,
        )
    return {"status": "recorded", "count": len(data.events)}
