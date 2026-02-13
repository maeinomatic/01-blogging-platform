from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List

from ..core.db import async_session
from ..models.post import Post

router = APIRouter(prefix="/api/posts", tags=["posts"])


async def get_db():
    async with async_session() as session:
        yield session


@router.get("/", response_model=List[Post])
async def list_posts(db: AsyncSession = Depends(get_db)):
    q = select(Post).where(Post.status == "published").order_by(Post.published_at.desc())
    result = await db.exec(q)
    return result.all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
async def create_post(payload: Post, db: AsyncSession = Depends(get_db)):
    db.add(payload)
    await db.commit()
    await db.refresh(payload)
    return payload


@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Post).where(Post.id == post_id)
    result = await db.exec(q)
    post = result.one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
