"""
Real-Time Events API (Server-Sent Events)

This module implements SSE endpoints for real-time updates to clients.
Events are broadcast via Redis Pub/Sub and streamed to connected clients.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["Real-Time Events"])

# Event types that clients can receive
EVENT_TYPES = [
    "notification.new",
    "message.new",
    "appointment.reminder",
    "appointment.updated",
    "document.processed",
    "document.scan_complete",
    "consent.required",
    "call.incoming",
    "call.completed",
    "impersonation.started",
    "impersonation.ended",
    "heartbeat",
]

# Organization-scoped event types
ORG_EVENT_TYPES = [
    "member.joined",
    "member.removed",
    "subscription.updated",
    "license.expiring",
]


class EventGenerator:
    """
    Generates SSE events from Redis Pub/Sub channels.

    This class manages the Redis subscription and converts
    Redis messages into the SSE wire format.
    """

    def __init__(
        self,
        user_id: str | None = None,
        organization_id: str | None = None,
        is_org_stream: bool = False,
    ):
        """
        Initialize the event generator.

        Args:
            user_id: User ID for user-scoped events
            organization_id: Organization ID for org-scoped events
            is_org_stream: If True, subscribe to org admin events
        """
        self.user_id = user_id
        self.organization_id = organization_id
        self.is_org_stream = is_org_stream
        self._redis: aioredis.Redis | None = None
        self._pubsub: aioredis.client.PubSub | None = None
        self._closed = False

    async def connect(self) -> None:
        """Establish Redis connection and subscribe to channels."""
        self._redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        self._pubsub = self._redis.pubsub()

        # Subscribe to relevant channels
        channels = []

        if self.is_org_stream and self.organization_id:
            # Admin stream: org-level events
            channels.append(f"org:{self.organization_id}:events")
        else:
            # User stream: user-level + public org events
            if self.user_id:
                channels.append(f"user:{self.user_id}")
            if self.organization_id:
                channels.append(f"org:{self.organization_id}:public")

        if channels:
            await self._pubsub.subscribe(*channels)
            logger.info(f"Subscribed to channels: {channels}")
        else:
            logger.warning("No channels to subscribe to")

    async def disconnect(self) -> None:
        """Clean up Redis connection."""
        self._closed = True
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
        logger.info("Disconnected from Redis Pub/Sub")

    def _format_sse(self, event_type: str, data: dict[str, Any]) -> str:
        """
        Format data as an SSE message.

        Args:
            event_type: The event type (e.g., 'notification.new')
            data: The event payload

        Returns:
            SSE formatted string
        """
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    async def generate(self) -> AsyncGenerator[str, None]:
        """
        Generate SSE events.

        Yields SSE formatted strings, including:
        - Heartbeats every 30 seconds
        - Messages from Redis Pub/Sub
        """
        heartbeat_interval = 30  # seconds
        last_heartbeat = datetime.utcnow()

        try:
            await self.connect()

            while not self._closed:
                if self._pubsub is None:
                    await asyncio.sleep(0.5)
                    continue

                try:
                    # Check for Redis messages with timeout
                    message = await asyncio.wait_for(
                        self._pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0,
                    )

                    if message and message["type"] == "message":
                        try:
                            # Parse the message data
                            payload = json.loads(message["data"])
                            event_type = payload.get("event_type", "unknown")
                            event_data = payload.get("data", {})

                            yield self._format_sse(event_type, event_data)

                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in Redis message: {message['data']}")

                except TimeoutError:
                    # No message received, continue to heartbeat check
                    pass
                except Exception as e:
                    logger.error(f"Error receiving Redis message: {e}")
                    # Small delay before retrying
                    await asyncio.sleep(0.5)

                # Send heartbeat if interval has passed
                now = datetime.utcnow()
                if (now - last_heartbeat).total_seconds() >= heartbeat_interval:
                    yield self._format_sse("heartbeat", {"timestamp": now.isoformat() + "Z"})
                    last_heartbeat = now

        except asyncio.CancelledError:
            logger.info("Event stream cancelled")
            raise
        finally:
            await self.disconnect()


async def get_current_user_from_token(
    request: Request,
    token: str | None = Query(None, description="JWT token for authentication"),
) -> dict[str, Any]:
    """
    Extract and validate user from JWT token.

    For SSE, the token can be passed as a query parameter
    since EventSource API doesn't support custom headers.

    Args:
        request: FastAPI request object
        token: Optional token from query parameter

    Returns:
        User info dict with id and organization_id

    Raises:
        HTTPException: If authentication fails
    """
    # First check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    # TODO: Implement proper JWT validation with Firebase Admin SDK
    # For now, we'll extract basic info for development/testing
    # In production, this should validate the token signature and expiry

    # Placeholder: In real implementation, decode and validate the JWT
    # For development, we'll accept a simple format or mock user
    try:
        # Try to decode as a simple JSON for development
        # Production should use firebase_admin.auth.verify_id_token(token)

        # Check if it's a mock token (for development)
        if token.startswith("dev_"):
            # Development token format: dev_{user_id}_{org_id}
            parts = token.split("_")
            if len(parts) >= 3:
                return {
                    "id": parts[1],
                    "organization_id": parts[2] if parts[2] != "none" else None,
                }

        # For actual JWT, we'd do something like:
        # from firebase_admin import auth
        # decoded = auth.verify_id_token(token)
        # return {
        #     "id": decoded["uid"],
        #     "organization_id": decoded.get("org_id"),
        # }

        # For now, reject unknown tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None


# Annotated dependency to avoid Depends in default argument
_UserDep = Depends(get_current_user_from_token)


@router.get("")
async def get_events(
    user: dict[str, Any] = _UserDep,
) -> StreamingResponse:
    """
    Server-Sent Events stream for real-time updates.

    This endpoint establishes a long-lived HTTP connection for
    server-to-client push notifications.

    The client will receive events such as:
    - notification.new: New notification created
    - message.new: New message in subscribed thread
    - appointment.reminder: Upcoming appointment reminder
    - appointment.updated: Appointment rescheduled/cancelled
    - document.processed: Document finished OCR/virus scan
    - document.scan_complete: Virus scan completed
    - consent.required: New consent document available
    - call.incoming: Incoming call (Call Center)
    - call.completed: Call ended
    - heartbeat: Keep-alive (every 30 seconds)

    Authentication can be provided via:
    - Authorization header: Bearer {token}
    - Query parameter: ?token={token}

    Returns:
        StreamingResponse with text/event-stream content type
    """
    generator = EventGenerator(
        user_id=user.get("id"),
        organization_id=user.get("organization_id"),
        is_org_stream=False,
    )

    return StreamingResponse(
        generator.generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/organizations/{org_id}")
async def get_org_events(
    org_id: str,
    user: dict[str, Any] = _UserDep,
) -> StreamingResponse:
    """
    Organization-scoped SSE stream for admin views.

    This endpoint provides organization-level events in addition
    to standard user events. Requires ADMIN or SUPER_ADMIN role.

    Additional event types:
    - member.joined: New member accepted invitation
    - member.removed: Member removed from organization
    - subscription.updated: Subscription status changed
    - license.expiring: Provider license expiring soon

    Args:
        org_id: Organization ID

    Returns:
        StreamingResponse with text/event-stream content type

    Raises:
        HTTPException: If user is not admin of the organization
    """
    # TODO: Verify user is ADMIN or SUPER_ADMIN of this org
    # For now, we'll check if the user's org matches
    if user.get("organization_id") != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this organization's event stream",
        )

    generator = EventGenerator(
        user_id=user.get("id"),
        organization_id=org_id,
        is_org_stream=True,
    )

    return StreamingResponse(
        generator.generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# =============================================================================
# Helper Functions for Publishing Events
# =============================================================================


async def publish_event(
    channel: str,
    event_type: str,
    data: dict[str, Any],
) -> None:
    """
    Publish an event to a Redis channel.

    This function is used by the worker and API to broadcast
    events to connected SSE clients.

    Args:
        channel: Redis channel name (e.g., 'user:123' or 'org:456:events')
        event_type: Event type string (e.g., 'notification.new')
        data: Event payload dictionary

    Example:
        await publish_event(
            channel="user:01HQ7V3X...",
            event_type="notification.new",
            data={"notification_id": "...", "title": "New Message"},
        )
    """
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    try:
        message = json.dumps(
            {
                "event_type": event_type,
                "data": data,
            }
        )
        await redis.publish(channel, message)
        logger.debug(f"Published {event_type} to {channel}")
    finally:
        await redis.close()


async def publish_user_event(
    user_id: str,
    event_type: str,
    data: dict[str, Any],
) -> None:
    """
    Publish an event to a specific user.

    Args:
        user_id: Target user ID
        event_type: Event type string
        data: Event payload
    """
    await publish_event(
        channel=f"user:{user_id}",
        event_type=event_type,
        data=data,
    )


async def publish_org_event(
    organization_id: str,
    event_type: str,
    data: dict[str, Any],
    is_public: bool = False,
) -> None:
    """
    Publish an event to an organization.

    Args:
        organization_id: Target organization ID
        event_type: Event type string
        data: Event payload
        is_public: If True, send to public channel (all org members)
                   If False, send to admin-only channel
    """
    suffix = "public" if is_public else "events"
    await publish_event(
        channel=f"org:{organization_id}:{suffix}",
        event_type=event_type,
        data=data,
    )
