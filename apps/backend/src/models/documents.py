"""Document model for patient file storage metadata."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .organizations import Organization
    from .profiles import Patient
    from .users import User


class Document(Base, UUIDMixin, TimestampMixin):
    """Model for patient documents stored in S3."""

    __tablename__ = "documents"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
    )
    uploaded_by_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)

    document_type: Mapped[str] = mapped_column(String(50), nullable=False, default="OTHER")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="documents")
    patient: Mapped["Patient"] = relationship(back_populates="documents")
    uploaded_by: Mapped["User"] = relationship()

    __table_args__ = (
        Index("ix_documents_patient_id", "patient_id"),
        Index("ix_documents_organization_id", "organization_id"),
        Index("ix_documents_document_type", "document_type"),
        Index("ix_documents_status", "status"),
    )
