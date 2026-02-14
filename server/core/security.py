from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt

from .config import settings
from .utils import get_utc_now

# Use Argon2 as the preferred password hashing scheme, while still accepting
# legacy bcrypt hashes so they can be verified and transparently re-hashed.
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated=["bcrypt"],
)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password (returns True/False). Use `pwd_context.needs_update` in
    the login flow to perform automatic re-hashing when the algorithm or
    parameters are outdated.
    """
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def needs_rehash(hashed: str) -> bool:
    """Return True when the stored hash should be upgraded to the current
    preferred algorithm/params.
    """
    return pwd_context.needs_update(hashed)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with timezone-aware expiration."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token with timezone-aware expiration."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode = {"sub": subject, "exp": expire, "typ": "refresh"}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return {}


def get_current_user_id(authorization: str) -> str:
    """Extract and validate user ID from Authorization header.
    
    Use as a FastAPI dependency with Header(..., alias="Authorization").
    Raises HTTPException(401) if the token is missing, invalid, or expired.
    """
    from fastapi import HTTPException
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    payload = decode_token(token)
    
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload["sub"]
