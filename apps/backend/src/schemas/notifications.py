from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    pass


class NotificationRead(BaseModel):
    id: UUID
    type: str  # APPOINTMENT, MESSAGE, SYSTEM, BILLING
    title: str
    body: str | None = None
    data_json: dict | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: list[NotificationRead]
    total: int
    unread_count: int
    page: int
    size: int


class UnreadCountResponse(BaseModel):
    count: int
