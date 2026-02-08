from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from typing import List

from ..models import Job, JobCreate, JobUpdate


class JobService:
    """Service for managing jobs."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_user_jobs(self, user_id: str) -> List[Job]:
        """Get all jobs for a user. Excludes chat_history for performance."""
        jobs = await self.db.jobs.find(
            {"user_id": user_id},
            {"_id": 0, "chat_history": 0}  # Exclude chat_history from list view
        ).sort("created_at", -1).to_list(100)

        for job in jobs:
            if isinstance(job.get("created_at"), str):
                job["created_at"] = datetime.fromisoformat(job["created_at"])
            if isinstance(job.get("updated_at"), str):
                job["updated_at"] = datetime.fromisoformat(job["updated_at"])

        return jobs

    async def create_job(self, user_id: str, job_data: JobCreate) -> Job:
        """Create a new job."""
        job = Job(
            user_id=user_id,
            title=job_data.title,
            notes=job_data.notes
        )

        doc = job.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        doc["updated_at"] = doc["updated_at"].isoformat()

        await self.db.jobs.insert_one(doc)
        return job

    async def get_job(self, job_id: str, user_id: str) -> Job:
        """Get a specific job."""
        job = await self.db.jobs.find_one(
            {"id": job_id, "user_id": user_id},
            {"_id": 0}
        )

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if isinstance(job.get("created_at"), str):
            job["created_at"] = datetime.fromisoformat(job["created_at"])
        if isinstance(job.get("updated_at"), str):
            job["updated_at"] = datetime.fromisoformat(job["updated_at"])

        return job

    async def update_job(
        self,
        job_id: str,
        user_id: str,
        update_data: JobUpdate
    ) -> Job:
        """Update a job."""
        job = await self.db.jobs.find_one(
            {"id": job_id, "user_id": user_id}
        )

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        update_dict = {}
        if update_data.title is not None:
            update_dict["title"] = update_data.title
        if update_data.status is not None:
            update_dict["status"] = update_data.status
        if update_data.notes is not None:
            update_dict["notes"] = update_data.notes
        if update_data.chat_history is not None:
            update_dict["chat_history"] = update_data.chat_history
        if update_data.chat_events is not None:
            update_dict["chat_events"] = update_data.chat_events
        if update_data.agent_job_id is not None:
            update_dict["agent_job_id"] = update_data.agent_job_id

        if update_dict:
            update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
            await self.db.jobs.update_one({"id": job_id}, {"$set": update_dict})

        updated = await self.db.jobs.find_one({"id": job_id}, {"_id": 0})

        if isinstance(updated.get("created_at"), str):
            updated["created_at"] = datetime.fromisoformat(updated["created_at"])
        if isinstance(updated.get("updated_at"), str):
            updated["updated_at"] = datetime.fromisoformat(updated["updated_at"])

        return updated

    async def delete_job(self, job_id: str, user_id: str) -> dict:
        """Delete a job."""
        result = await self.db.jobs.delete_one(
            {"id": job_id, "user_id": user_id}
        )

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"message": "Job deleted"}
