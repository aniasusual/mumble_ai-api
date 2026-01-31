from fastapi import APIRouter
from .auth import router as auth_router
from .sessions import router as jobs_router
from .chat import router as chat_router
from .waitlist import router as waitlist_router


api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(waitlist_router, prefix="/waitlist", tags=["waitlist"])

__all__ = ["api_router"]
