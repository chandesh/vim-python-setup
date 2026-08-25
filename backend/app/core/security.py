"""Password hashing and JWT token utilities."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Credentials exception reused by auth flows
CREDENTIALS_EXCEPTION_MESSAGE = "Could not validate credentials"


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token for the given user.

    Args:
        user_id: ID of the authenticated user (stored as `sub` claim)
        expires_delta: Optional custom lifetime; defaults to settings

    Returns:
        Encoded JWT string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[str]:
    """Decode and validate a JWT access token.

    Args:
        token: Encoded JWT string

    Returns:
        The subject (user ID) claim, or None if the token is invalid/expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        return sub
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


def get_token_expire_seconds() -> int:
    """Return the configured token lifetime in seconds."""
    return settings.access_token_expire_minutes * 60
