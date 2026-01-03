from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List


class CareTeamAssignmentCreate(BaseModel):
    """Create a care team assignment for a patient."""
    provider_id: UUID = Field(..., description="Provider to assign")
    role: str = Field(
        default="SPECIALIST",
        description="Role in care team: PRIMARY, SPECIALIST, or CONSULTANT"
    )

    @classmethod
    def validate_role(cls, value: str) -> str:
        valid_roles = {"PRIMARY", "SPECIALIST", "CONSULTANT"}
        if value.upper() not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return value.upper()


class CareTeamProviderInfo(BaseModel):
    """Embedded provider information for care team responses."""
    id: UUID
    user_id: UUID
    npi_number: Optional[str] = None
    specialty: Optional[str] = None
    user_display_name: Optional[str] = None
    user_email: Optional[str] = None


class CareTeamAssignmentRead(BaseModel):
    """Read a care team assignment with provider details."""
    id: UUID
    patient_id: UUID
    provider_id: UUID
    role: str
    assigned_at: datetime
    removed_at: Optional[datetime] = None
    provider: CareTeamProviderInfo
    
    model_config = {"from_attributes": True}


class CareTeamMember(BaseModel):
    """Compact care team member for list views."""
    assignment_id: UUID
    provider_id: UUID
    role: str
    assigned_at: datetime
    provider_name: Optional[str] = None
    provider_specialty: Optional[str] = None
    provider_npi: Optional[str] = None


class CareTeamList(BaseModel):
    """Full care team response with all members."""
    patient_id: UUID
    members: List[CareTeamMember]
    primary_provider: Optional[CareTeamMember] = None
