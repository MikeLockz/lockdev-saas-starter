from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid

if TYPE_CHECKING:
    from app.models.profile import Patient


class ContactMethod(Base, TimestampMixin):
    __tablename__ = "contact_methods"

    id: Mapped[pk_ulid]
    patient_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("patients.id"), index=True
    )
    type: Mapped[str] = mapped_column(String(20))  # PHONE, EMAIL, SMS
    value: Mapped[str] = mapped_column(String(255))
    label: Mapped[str | None] = mapped_column(String(50))  # Home, Work, Mobile
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_safe_for_voicemail: Mapped[bool] = mapped_column(Boolean, default=False)

    patient: Mapped["Patient"] = relationship(back_populates="contact_methods")
