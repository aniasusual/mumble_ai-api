from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from ...core import get_db, get_current_user
from ...models import LearningSession, SessionCreate, SessionUpdate
from ...services import SessionService


router = APIRouter()


@router.get("", response_model=List[LearningSession])
async def get_sessions(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all sessions for current user."""
    session_service = SessionService(db)
    return await session_service.get_user_sessions(current_user["id"])


@router.post("", response_model=LearningSession)
async def create_session(
    session_data: SessionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new learning session."""
    session_service = SessionService(db)
    return await session_service.create_session(current_user["id"], session_data)


@router.get("/{session_id}", response_model=LearningSession)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific session."""
    session_service = SessionService(db)
    return await session_service.get_session(session_id, current_user["id"])


@router.put("/{session_id}", response_model=LearningSession)
async def update_session(
    session_id: str,
    update_data: SessionUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a session."""
    session_service = SessionService(db)
    return await session_service.update_session(session_id, current_user["id"], update_data)


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a session."""
    session_service = SessionService(db)
    return await session_service.delete_session(session_id, current_user["id"])
