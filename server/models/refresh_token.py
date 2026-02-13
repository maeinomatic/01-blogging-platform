from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field


class RefreshToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    token_hash: str
    user_agent: str | None = None
    ip: str | None = None
    expires_at: datetime | None = None
    revoked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
