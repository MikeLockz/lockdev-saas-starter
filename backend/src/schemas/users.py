from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_super_admin: bool
    full_name: Optional[str] = None
    role: str = "guest"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
