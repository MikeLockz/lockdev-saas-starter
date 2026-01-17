from typing import Any

from pydantic import BaseModel, Field


class TelemetryEvent(BaseModel):
    event: str = Field(..., description="Name of the event", examples=["page_view"])
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Additional properties of the event"
    )


class TelemetryBatch(BaseModel):
    events: list[TelemetryEvent]
