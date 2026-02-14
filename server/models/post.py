from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import SQLModel, Field
from typing import Optional, Any, Dict
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


# Import get_utc_now from core utils at module level would create circular import
# So we define a module-level function that can be used as default_factory
def _default_created_at():
    """Default factory for created_at field."""
    from ..core.utils import get_utc_now
    return get_utc_now()


class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    author_id: UUID = Field(foreign_key="user.id")
    title: str
    slug: str
    short_id: Optional[str] = Field(default=None, index=True)
    status: str = "draft"
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    content_html: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    comments_count: int = 0
    likes_count: int = 0
    created_at: datetime = Field(default_factory=_default_created_at)
    updated_at: Optional[datetime] = None
