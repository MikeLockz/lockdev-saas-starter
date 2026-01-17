import asyncio

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter()


@router.get("")
async def stream_events(request: Request):
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
