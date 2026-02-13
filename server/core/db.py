from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# convenience import for Alembic autogenerate
metadata = SQLModel.metadata

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
