from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models_base import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, pk_ulid

if TYPE_CHECKING:
    from app.models.profile import Patient, Provider


class CareTeamAssignment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "care_team_assignments"

    id: Mapped[pk_ulid]
    patient_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("patients.id"), index=True
    )
    provider_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("providers.id"), index=True
    )
    role: Mapped[str] = mapped_column(
        String(50), default="primary"
    )  # PRIMARY, SECONDARY, etc.

    patient: Mapped["Patient"] = relationship()
    provider: Mapped["Provider"] = relationship()
