from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field


class Bookmark(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    post_id: UUID = Field(foreign_key="post.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {"unique": ["user_id", "post_id"]}
    }
