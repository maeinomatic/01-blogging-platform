from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import SQLModel, Field


# Import get_utc_now from core utils at module level would create circular import
# So we define a module-level function that can be used as default_factory
def _default_created_at():
    """Default factory for created_at field."""
    from ..core.utils import get_utc_now
    return get_utc_now()


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
    created_at: datetime = Field(default_factory=_default_created_at)
    updated_at: Optional[datetime] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID
    created_at: datetime
