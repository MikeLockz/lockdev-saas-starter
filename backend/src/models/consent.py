from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .mixins import UUIDMixin, TimestampMixin

class ConsentDocument(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "consent_documents"

    # TOS, HIPAA, PRIVACY
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False) 
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    content_url: Mapped[Optional[str]] = mapped_column(String(500))
    content_text: Mapped[Optional[str]] = mapped_column(String)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    signatures: Mapped[list["UserConsent"]] = relationship(back_populates="document")


class UserConsent(Base, UUIDMixin):
    __tablename__ = "user_consents"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("consent_documents.id"), nullable=False, index=True)
    
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45)) # IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    document: Mapped["ConsentDocument"] = relationship(back_populates="signatures")
    # user relationship is likely defined in User model or needs to be added there if we want backref
    # For now, we can leave it unilateral or add it here if needed.
    # But User model is in users.py. We can import if needed, but avoiding circular imports is good.
    # We can use string reference "User".
    user: Mapped["User"] = relationship("User", back_populates="consents")
