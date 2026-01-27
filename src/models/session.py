from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class LearningSession(BaseModel):
    """Learning session model."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: Optional[str] = None
    status: str = "active"  # active, completed, paused
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None
    chat_history: Optional[List[dict]] = None
    agent_session_id: Optional[str] = None  # AgentOS session ID for continuity


class SessionCreate(BaseModel):
    """Session creation model."""
    title: Optional[str] = None
    notes: Optional[str] = None


class SessionUpdate(BaseModel):
    """Session update model."""
    title: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    chat_history: Optional[List[dict]] = None
    agent_session_id: Optional[str] = None
