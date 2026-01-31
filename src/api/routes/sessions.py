from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from ...core import get_db, get_current_user
from ...models import Job, JobCreate, JobUpdate
from ...services import JobService


router = APIRouter()


@router.get("", response_model=List[Job])
async def get_jobs(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all jobs for current user."""
    job_service = JobService(db)
    return await job_service.get_user_jobs(current_user["id"])


@router.post("", response_model=Job)
async def create_job(
    job_data: JobCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new job."""
    job_service = JobService(db)
    return await job_service.create_job(current_user["id"], job_data)


@router.get("/{job_id}", response_model=Job)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific job."""
    job_service = JobService(db)
    return await job_service.get_job(job_id, current_user["id"])


@router.put("/{job_id}", response_model=Job)
async def update_job(
    job_id: str,
    update_data: JobUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a job."""
    job_service = JobService(db)
    return await job_service.update_job(job_id, current_user["id"], update_data)


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a job."""
    job_service = JobService(db)
    return await job_service.delete_job(job_id, current_user["id"])
