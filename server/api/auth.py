from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from ..core.db import async_session
from ..core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from ..models.user import User, UserCreate

router = APIRouter(prefix="/api/auth", tags=["auth"])


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    q = select(User).where(User.email == user_in.email)
    existing = await db.exec(q)
    if existing.one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=user_in.email, username=user_in.username, password_hash=get_password_hash(user_in.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/login")
async def login(form_data: UserCreate, db: AsyncSession = Depends(get_db)):
    q = select(User).where(User.email == form_data.email)
    result = await db.exec(q)
    user = result.one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
