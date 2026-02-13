from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.db import async_session
from ..models.comment import Comment

router = APIRouter(prefix="/api/posts/{post_id}/comments", tags=["comments"])


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_comment(post_id: str, payload: Comment, db: AsyncSession = Depends(get_db)):
    payload.post_id = post_id
    db.add(payload)
    await db.commit()
    await db.refresh(payload)
    return payload
