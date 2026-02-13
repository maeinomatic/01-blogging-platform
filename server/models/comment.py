from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import SQLModel, Field


class Comment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    post_id: UUID = Field(foreign_key="post.id")
    author_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    parent_id: Optional[UUID] = Field(default=None, foreign_key="comment.id")
    content: str
    is_moderated: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
