from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class Job(BaseModel):
    """Job model."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: Optional[str] = None
    status: str = "active"  # active, completed, paused
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None
    chat_history: Optional[List[dict]] = None
    chat_events: Optional[List[dict]] = None
    agent_job_id: Optional[str] = None  # AgentOS session ID (job identifier)


class JobCreate(BaseModel):
    """Job creation model."""
    title: Optional[str] = None
    notes: Optional[str] = None


class JobUpdate(BaseModel):
    """Job update model."""
    title: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    chat_history: Optional[List[dict]] = None
    chat_events: Optional[List[dict]] = None
    agent_job_id: Optional[str] = None
