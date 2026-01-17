import datetime
from typing import Annotated

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from ulid import ULID


def generate_ulid():
    return str(ULID())


# Re-usable types
pk_ulid = Annotated[
    str, mapped_column(String(26), primary_key=True, default=generate_ulid)
]


class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
