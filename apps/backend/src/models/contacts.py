from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .profiles import Patient


class ContactMethod(Base, UUIDMixin, TimestampMixin):
    """Contact method for a patient (phone, email, SMS).

    The `is_safe_for_voicemail` flag is CRITICAL for HIPAA compliance -
    it indicates whether PHI can be left in a voicemail at this number.
    """

    __tablename__ = "contact_methods"

    patient_id: Mapped[UUID] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # MOBILE, HOME, EMAIL
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_safe_for_voicemail: Mapped[bool] = mapped_column(Boolean, default=False)  # HIPAA Critical
    label: Mapped[str | None] = mapped_column(String(50))  # Home, Work, Mobile

    # Relationships
    patient: Mapped["Patient"] = relationship(back_populates="contact_methods")
