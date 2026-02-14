from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, select
from typing import Any, List
from datetime import datetime, timezone
from uuid import UUID
import re
from sqlalchemy import String

from ..core.db import async_session
from ..models.post import Post

router = APIRouter(prefix="/api/posts", tags=["posts"])


def slugify_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9\s-]", "", title.lower().strip())
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug or "post"


def build_post_slug(title: str, post_id: UUID) -> str:
    # Use the slugified title only. The post UUID is already present in the
    # canonical URL (/posts/{postId}/{slug}) so appending a short id to the
    # slug is duplicated and unnecessary.
    return slugify_title(title)


def parse_published_at(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = value.strip()
        if text.endswith("Z"):
            text = text.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid published_at datetime format") from exc

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


class PostCreate(SQLModel):
    author_id: UUID | str
    title: str
    status: str = "draft"
    published_at: datetime | str | None = None
    summary: str | None = None
    content_html: str | None = None
    content_json: dict[str, Any] | None = None


class PostUpdate(SQLModel):
    title: str | None = None
    status: str | None = None
    published_at: datetime | str | None = None
    summary: str | None = None
    content_html: str | None = None


async def get_db():
    async with async_session() as session:
        yield session


@router.get("/", response_model=List[Post])
async def list_posts(db: AsyncSession = Depends(get_db)):
    q = select(Post).order_by(Post.created_at.desc())
    result = await db.exec(q)
    return result.all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
async def create_post(payload: PostCreate, db: AsyncSession = Depends(get_db)):
    published_at = parse_published_at(payload.published_at)
    if payload.status == "published" and published_at is None:
        published_at = datetime.utcnow()
    if payload.status != "published":
        published_at = None

    post = Post(
        author_id=payload.author_id,
        title=payload.title,
        slug="",
        status=payload.status,
        published_at=published_at,
        summary=payload.summary,
        content_html=payload.content_html,
        content_json=payload.content_json,
    )

    post.slug = build_post_slug(post.title, post.id)
    # persist short_id (first UUID segment) for fast indexed lookup
    post.short_id = str(post.id).split("-")[0]

    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Post).where(Post.id == post_id)
    result = await db.exec(q)
    post = result.one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/short/{short_id}", response_model=Post)
async def get_post_by_short(short_id: str, db: AsyncSession = Depends(get_db)):
    """Lookup post by a short prefix of the UUID (e.g. first 8 chars).

    Returns 404 when not found and 409 if the short id is ambiguous.
    """
    if not re.fullmatch(r"[0-9a-fA-F]{2,32}", short_id):
        raise HTTPException(status_code=400, detail="Invalid short id")

    # prefer exact short_id match (uses new indexed column); fallback to UUID-prefix lookup
    q = select(Post).where(Post.short_id == short_id)
    result = await db.exec(q)
    matches = result.all()
    if not matches:
        q = select(Post).where(Post.id.cast(String).like(f"{short_id}%"))
        result = await db.exec(q)
        matches = result.all()

    if not matches:
        raise HTTPException(status_code=404, detail="Post not found")
    if len(matches) > 1:
        raise HTTPException(status_code=409, detail="Short id ambiguous")
    return matches[0]


@router.put("/{post_id}", response_model=Post)
async def update_post(post_id: str, payload: PostUpdate, db: AsyncSession = Depends(get_db)):
    q = select(Post).where(Post.id == post_id)
    result = await db.exec(q)
    post = result.one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    updates = payload.model_dump(exclude_unset=True)
    if "published_at" in updates:
        updates["published_at"] = parse_published_at(updates["published_at"])

    for key, value in updates.items():
        setattr(post, key, value)

    if post.status == "published" and post.published_at is None:
        post.published_at = datetime.utcnow()
    if post.status != "published":
        post.published_at = None

    post.updated_at = datetime.utcnow()
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post
