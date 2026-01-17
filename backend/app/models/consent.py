from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid


class ConsentDocument(Base, TimestampMixin):
    __tablename__ = "consent_documents"

    id: Mapped[pk_ulid]
    type: Mapped[str] = mapped_column(String(50), index=True)  # TOS, HIPAA, etc.
    version: Mapped[int] = mapped_column(Integer, default=1)
    content: Mapped[str] = mapped_column(String)  # Or link to document

    # Relationships
    user_consents: Mapped[list["UserConsent"]] = relationship(back_populates="document")


class UserConsent(Base, TimestampMixin):
    __tablename__ = "user_consents"

    id: Mapped[pk_ulid]
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), index=True)
    document_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("consent_documents.id"), index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(255))

    document: Mapped["ConsentDocument"] = relationship(back_populates="user_consents")
