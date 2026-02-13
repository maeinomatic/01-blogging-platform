from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class Media(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    uploader_id: UUID = Field(foreign_key="user.id")
    url: str
    meta: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
