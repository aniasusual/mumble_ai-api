from pydantic import BaseModel, Field
import uuid


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
