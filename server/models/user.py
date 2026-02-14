from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


def _get_utc_now():
    """Get current UTC datetime without timezone info (naive datetime)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class UserBase(SQLModel):
    email: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=_get_utc_now)
    updated_at: Optional[datetime] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID
    created_at: datetime
