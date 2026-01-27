from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...core import get_db, get_current_user
from ...models import UserCreate, UserLogin, TokenResponse, UserResponse, UserUpdate
from ...services import AuthService


router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Register a new user."""
    auth_service = AuthService(db)
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Login user."""
    auth_service = AuthService(db)
    return await auth_service.login_user(login_data)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current user profile."""
    auth_service = AuthService(db)
    return await auth_service.get_user_profile(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update current user profile."""
    auth_service = AuthService(db)
    return await auth_service.update_user_profile(current_user, update_data)
