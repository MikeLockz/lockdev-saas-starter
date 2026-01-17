from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, pk_ulid


class Document(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "documents"

    id: Mapped[pk_ulid]
    organization_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id"), index=True
    )
    patient_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("patients.id"), index=True
    )

    filename: Mapped[str] = mapped_column(String(255))
    s3_key: Mapped[str] = mapped_column(String(512), unique=True)
    file_size: Mapped[int | None] = mapped_column(Integer)
    content_type: Mapped[str | None] = mapped_column(String(100))

    document_type: Mapped[str | None] = mapped_column(
        String(50)
    )  # LAB_REPORT, CONSENT, etc.
    status: Mapped[str] = mapped_column(
        String(20), default="UPLOADED"
    )  # UPLOADED, PROCESSED, ERROR

    organization: Mapped["Organization"] = relationship()
    patient: Mapped["Patient"] = relationship()
