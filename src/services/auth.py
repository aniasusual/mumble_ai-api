from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
import uuid

from ..core import hash_password, verify_password, create_access_token
from ..models import UserCreate, UserLogin, TokenResponse, UserResponse, UserUpdate


class AuthService:
    """Authentication service for user management."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        """Register a new user."""
        # Check if user exists
        existing = await self.db.users.find_one({"email": user_data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "password_hash": hash_password(user_data.password),
            "avatar_url": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        await self.db.users.insert_one(user_doc)

        # Create token
        token = create_access_token(user_id)

        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user_id,
                email=user_data.email,
                name=user_data.name,
                avatar_url=None,
                created_at=datetime.now(timezone.utc)
            )
        )

    async def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return token."""
        user = await self.db.users.find_one({"email": login_data.email})

        if not user or not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token(user["id"])

        created_at = user["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                avatar_url=user.get("avatar_url"),
                created_at=created_at
            )
        )

    async def get_user_profile(self, user: dict) -> UserResponse:
        """Get user profile."""
        created_at = user["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            avatar_url=user.get("avatar_url"),
            created_at=created_at
        )

    async def update_user_profile(self, user: dict, update_data: UserUpdate) -> UserResponse:
        """Update user profile."""
        update_dict = {}
        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.avatar_url is not None:
            update_dict["avatar_url"] = update_data.avatar_url

        if update_dict:
            update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
            await self.db.users.update_one({"id": user["id"]}, {"$set": update_dict})

        updated_user = await self.db.users.find_one({"id": user["id"]})
        created_at = updated_user["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return UserResponse(
            id=updated_user["id"],
            email=updated_user["email"],
            name=updated_user["name"],
            avatar_url=updated_user.get("avatar_url"),
            created_at=created_at
        )
