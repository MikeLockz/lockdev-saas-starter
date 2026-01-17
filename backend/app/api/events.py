import asyncio

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("")
async def stream_events(
    request: Request, current_user: User = Depends(get_current_user)
):
    """
    Server-Sent Events endpoint for real-time updates.
    """

    async def event_generator():
        while True:
            # Check if client is still connected
            if await request.is_disconnected():
                break

            # Placeholder for real event logic (e.g. Redis Pub/Sub)
            yield {"event": "ping", "data": "heartbeat"}

            await asyncio.sleep(15)

    return EventSourceResponse(event_generator())
