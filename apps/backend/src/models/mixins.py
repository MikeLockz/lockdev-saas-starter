"""
Reusable SQLAlchemy Mixins for Database Models.

These mixins provide common functionality across models:
- UUIDMixin: ULID-based primary keys for time-sortable unique IDs
- TimestampMixin: Automatic created_at/updated_at tracking
- SoftDeleteMixin: Logical deletion support for data retention
"""

import uuid
from datetime import datetime

import ulid
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Provides a ULID-based UUID primary key.

    Uses ULID (Universally Unique Lexicographically Sortable Identifier)
    which provides time-sorted UUIDs for better index performance.
    """

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=lambda: ulid.ULID().to_uuid())


class TimestampMixin:
    """Provides automatic timestamp tracking.

    Adds created_at (set once on insert) and updated_at (updated on every change)
    columns. Uses server_default for consistent timestamps across the cluster.
    """

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    """Provides soft-delete functionality for data retention.

    Instead of permanently deleting records, sets deleted_at timestamp.
    Use the is_deleted property to check deletion status.
    Queries should filter on deleted_at IS NULL for active records.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
