from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Tag(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    slug: str
