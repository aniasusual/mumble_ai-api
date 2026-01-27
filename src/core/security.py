from datetime import datetime, timezone, timedelta
from typing import Optional
import hashlib
import jwt
import bcrypt
from .config import settings


def _preprocess_password(password: str) -> bytes:
    """Pre-hash password with SHA256 to handle bcrypt's 72-byte limit."""
    return hashlib.sha256(password.encode('utf-8')).digest()


def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    preprocessed = _preprocess_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(preprocessed, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    preprocessed = _preprocess_password(plain_password)
    return bcrypt.checkpw(preprocessed, hashed_password.encode('utf-8'))


def create_access_token(user_id: str) -> str:
    """Create a JWT access token for a user."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Decode a JWT token and return the user ID."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
