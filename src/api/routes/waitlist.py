from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...core import get_db
from ...models import WaitlistEntry, WaitlistCreate


router = APIRouter()


@router.post("", response_model=WaitlistEntry)
async def join_waitlist(
    waitlist_data: WaitlistCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Join the waitlist."""
    existing = await db.waitlist.find_one({"email": waitlist_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already on waitlist")

    entry = WaitlistEntry(email=waitlist_data.email)
    doc = entry.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()

    await db.waitlist.insert_one(doc)
    return entry


@router.get("/check/{email}")
async def check_waitlist(
    email: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Check if email is on waitlist."""
    existing = await db.waitlist.find_one({"email": email})
    return {"exists": existing is not None}
