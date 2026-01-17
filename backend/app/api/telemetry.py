import structlog
from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger("analytics")


@router.post("")
async def track_event(data: dict, current_user: User = Depends(get_current_user)):
    """
    Records a single behavioral event.
    """
    logger.info("ANALYTICS_EVENT", user_id=current_user.id, **data)
    return {"status": "recorded"}


@router.post("/batch")
async def track_events_batch(
    events: list[dict], current_user: User = Depends(get_current_user)
):
    """
    Records a batch of behavioral events.
    """
    for event in events:
        logger.info("ANALYTICS_EVENT", user_id=current_user.id, **event)
    return {"status": "recorded", "count": len(events)}
