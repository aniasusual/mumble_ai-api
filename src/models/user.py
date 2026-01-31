from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)
    base_language: Optional[str] = "English"


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""
    model_config = ConfigDict(extra="ignore")

    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    base_language: Optional[str] = "English"
    created_at: datetime


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    """User update model."""
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    base_language: Optional[str] = None
