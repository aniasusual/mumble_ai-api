import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str
    MONGODB_DATABASE: str = "mumble_ai"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # LLM Keys
    EMERGENT_LLM_KEY: str
    EMERGENT_PROXY: Optional[str] = "https://proxy.dev.emergentagent.com/llm"
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # JWT Authentication
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # API
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Mumble AI"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
