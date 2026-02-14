from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import SQLModel, Field
from typing import Optional, Any, Dict
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
