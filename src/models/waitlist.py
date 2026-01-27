from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime, timezone
import uuid


class WaitlistEntry(BaseModel):
    """Waitlist entry model."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WaitlistCreate(BaseModel):
    """Waitlist creation model."""
    email: EmailStr
