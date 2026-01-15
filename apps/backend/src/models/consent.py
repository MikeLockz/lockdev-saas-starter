"""
Legal Consent Tracking for HIPAA Compliance.

This module implements formal consent document management for legal/regulatory
compliance (TOS, HIPAA Authorization, Privacy Policy).

NOTE: This is DIFFERENT from communication preferences on the User model:
    - User.transactional_consent / marketing_consent = TCPA email preferences
    - UserConsent = Legal document signatures with audit metadata

For communication preferences, see apps/backend/src/models/users.py
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin


class ConsentDocument(Base, UUIDMixin, TimestampMixin):
    """
    A versioned legal document that users must sign.

    Document types include:
        - TOS: Terms of Service
        - HIPAA: HIPAA Authorization
        - PRIVACY: Privacy Policy

    Only documents with is_active=True require user signatures.
    When a new version is published, set the old version to is_active=False.
    """

    __tablename__ = "consent_documents"

    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)  # TOS, HIPAA, PRIVACY
    version: Mapped[str] = mapped_column(String(50), nullable=False)

    content_url: Mapped[str | None] = mapped_column(String(500))
    content_text: Mapped[str | None] = mapped_column(String)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    signatures: Mapped[list["UserConsent"]] = relationship(back_populates="document")


class UserConsent(Base, UUIDMixin):
    """
    Record of a user signing a legal consent document.

    This provides legal proof of consent with:
        - Timestamp of signature (database-generated for accuracy)
        - IP address at time of signing
        - User agent (browser/device info)

    NOTE: This is separate from User.transactional_consent/marketing_consent
    which are boolean flags for TCPA email preferences.
    """

    __tablename__ = "user_consents"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("consent_documents.id"), nullable=False, index=True)

    # Use server_default for consistent timestamp (not Python-side default)
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6
    user_agent: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    document: Mapped["ConsentDocument"] = relationship(back_populates="signatures")
    # user relationship is likely defined in User model or needs to be added there if we want backref
    # For now, we can leave it unilateral or add it here if needed.
    # But User model is in users.py. We can import if needed, but avoiding circular imports is good.
    # We can use string reference "User".
    user: Mapped["User"] = relationship("User", back_populates="consents")
