from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None
    auth_provider: str = "LOCAL"
    avatar_url: str | None = None
    email_verified: bool = False
