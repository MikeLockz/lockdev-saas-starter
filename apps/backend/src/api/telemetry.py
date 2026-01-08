"""
Telemetry API

This module provides endpoints for behavioral analytics and user tracking.
Events are logged using structlog for CloudWatch ingestion.
# TEST: post-commit hook trigger
"""

import logging
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.database import tenant_id_ctx, user_id_ctx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


class TelemetryEvent(BaseModel):
    """Telemetry event payload from the frontend."""

    event_name: str = Field(..., min_length=1, max_length=100)
    properties: dict[str, Any] = Field(default_factory=dict)


class TelemetryResponse(BaseModel):
    """Response confirming event was logged."""

    success: bool = True
    event_id: str | None = None


@router.post("", response_model=TelemetryResponse)
async def log_telemetry_event(
    event: TelemetryEvent,
    request: Request,
) -> TelemetryResponse:
    """
    Log a behavioral analytics event.

    This endpoint accepts telemetry events from the frontend and logs them
    using structlog with `event_type="analytics"` for CloudWatch filtering.

    **Use Cases:**
    - Page views and navigation patterns
    - Feature usage tracking
    - Button clicks and user interactions
    - Error events (client-side)
    - Performance metrics

    **Privacy:**
    - Do not send PII/PHI in the properties
    - User ID is automatically attached from context
    - IP address is logged for basic analytics

    Args:
        event: The telemetry event with name and properties

    Returns:
        Confirmation that the event was logged
    """
    # Get user context
    user_id = user_id_ctx.get()
    tenant_id = tenant_id_ctx.get()

    # Extract request metadata
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")

    # Log the event with structured data
    logger.info(
        f"Telemetry event: {event.event_name}",
        extra={
            "event_type": "analytics",
            "event_name": event.event_name,
            "properties": event.properties,
            "actor_id": user_id,
            "org_id": tenant_id,
            "ip_address": client_ip,
            "user_agent": user_agent[:200] if user_agent else None,  # Truncate UA
        },
    )

    return TelemetryResponse(success=True)


@router.post("/batch", response_model=TelemetryResponse)
async def log_telemetry_batch(
    events: list[TelemetryEvent],
    request: Request,
) -> TelemetryResponse:
    """
    Log multiple telemetry events in a batch.

    This endpoint is optimized for sending multiple events at once,
    reducing the number of HTTP requests from the frontend.

    **Use Cases:**
    - Offline event buffering
    - Page unload event flushing
    - Session aggregation

    Args:
        events: List of telemetry events

    Returns:
        Confirmation that all events were logged
    """
    if not events:
        return TelemetryResponse(success=True)

    # Limit batch size
    MAX_BATCH_SIZE = 100
    events_to_process = events[:MAX_BATCH_SIZE]

    # Get user context
    user_id = user_id_ctx.get()
    tenant_id = tenant_id_ctx.get()

    # Extract request metadata
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")

    # Log each event
    for event in events_to_process:
        logger.info(
            f"Telemetry event: {event.event_name}",
            extra={
                "event_type": "analytics",
                "event_name": event.event_name,
                "properties": event.properties,
                "actor_id": user_id,
                "org_id": tenant_id,
                "ip_address": client_ip,
                "user_agent": user_agent[:200] if user_agent else None,
            },
        )

    logger.info(
        "Telemetry batch processed",
        extra={
            "event_type": "analytics",
            "batch_size": len(events_to_process),
            "actor_id": user_id,
        },
    )

    return TelemetryResponse(success=True)
