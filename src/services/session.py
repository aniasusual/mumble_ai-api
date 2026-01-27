from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from typing import List

from ..models import LearningSession, SessionCreate, SessionUpdate


class SessionService:
    """Service for managing learning sessions."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_user_sessions(self, user_id: str) -> List[LearningSession]:
        """Get all sessions for a user."""
        sessions = await self.db.sessions.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)

        for session in sessions:
            if isinstance(session.get("created_at"), str):
                session["created_at"] = datetime.fromisoformat(session["created_at"])
            if isinstance(session.get("updated_at"), str):
                session["updated_at"] = datetime.fromisoformat(session["updated_at"])

        return sessions

    async def create_session(self, user_id: str, session_data: SessionCreate) -> LearningSession:
        """Create a new learning session."""
        session = LearningSession(
            user_id=user_id,
            title=session_data.title,
            notes=session_data.notes
        )

        doc = session.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        doc["updated_at"] = doc["updated_at"].isoformat()

        await self.db.sessions.insert_one(doc)
        return session

    async def get_session(self, session_id: str, user_id: str) -> LearningSession:
        """Get a specific session."""
        session = await self.db.sessions.find_one(
            {"id": session_id, "user_id": user_id},
            {"_id": 0}
        )

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if isinstance(session.get("created_at"), str):
            session["created_at"] = datetime.fromisoformat(session["created_at"])
        if isinstance(session.get("updated_at"), str):
            session["updated_at"] = datetime.fromisoformat(session["updated_at"])

        return session

    async def update_session(
        self,
        session_id: str,
        user_id: str,
        update_data: SessionUpdate
    ) -> LearningSession:
        """Update a session."""
        session = await self.db.sessions.find_one(
            {"id": session_id, "user_id": user_id}
        )

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        update_dict = {}
        if update_data.title is not None:
            update_dict["title"] = update_data.title
        if update_data.status is not None:
            update_dict["status"] = update_data.status
        if update_data.notes is not None:
            update_dict["notes"] = update_data.notes
        if update_data.chat_history is not None:
            update_dict["chat_history"] = update_data.chat_history

        if update_dict:
            update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
            await self.db.sessions.update_one({"id": session_id}, {"$set": update_dict})

        updated = await self.db.sessions.find_one({"id": session_id}, {"_id": 0})

        if isinstance(updated.get("created_at"), str):
            updated["created_at"] = datetime.fromisoformat(updated["created_at"])
        if isinstance(updated.get("updated_at"), str):
            updated["updated_at"] = datetime.fromisoformat(updated["updated_at"])

        return updated

    async def delete_session(self, session_id: str, user_id: str) -> dict:
        """Delete a session."""
        result = await self.db.sessions.delete_one(
            {"id": session_id, "user_id": user_id}
        )

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": "Session deleted"}
