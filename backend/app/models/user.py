from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import TimestampMixin, pk_ulid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[pk_ulid]
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # HIPAA / Security
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255))
    mfa_backup_codes: Mapped[dict | None] = mapped_column(JSON)
    timezone: Mapped[str | None] = mapped_column(String(50))

    # Consent
    communication_consent_sms: Mapped[bool] = mapped_column(Boolean, default=False)

    # Profiles
    provider_profile: Mapped["Provider"] = relationship(
        back_populates="user", uselist=False, primaryjoin="User.id == Provider.user_id"
    )
    staff_profile: Mapped["Staff"] = relationship(
        back_populates="user", uselist=False, primaryjoin="User.id == Staff.user_id"
    )
    patient_profile: Mapped["Patient"] = relationship(
        back_populates="user",
        uselist=False,
        primaryjoin="User.id == Patient.user_id",
        foreign_keys="Patient.user_id",
    )
