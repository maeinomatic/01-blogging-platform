from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from fastapi import Request
from ..core.db import async_session
from ..core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from ..models.user import User, UserCreate
from ..models.refresh_token import RefreshToken
from ..core.config import settings
from sqlmodel import SQLModel
import hashlib
from datetime import datetime, timedelta

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
async def login(form_data: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    q = select(User).where(User.email == form_data.email)
    result = await db.exec(q)
    user = result.one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # If hash needs upgrade (e.g. bcrypt -> argon2), re-hash and persist the new hash
    from ..core.security import needs_rehash

    if needs_rehash(user.password_hash):
        user.password_hash = get_password_hash(form_data.password)
        db.add(user)
        await db.commit()

    # create tokens
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))

    # persist refresh token (store hash only)
    token_hash = hashlib.sha256(refresh.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(user_id=user.id, token_hash=token_hash, user_agent=request.headers.get("user-agent"), ip=(request.client.host if request.client else None), expires_at=expires_at)
    db.add(rt)
    await db.commit()

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


class _RefreshIn(SQLModel):
    refresh_token: str


@router.post("/refresh")
async def refresh_token(payload: _RefreshIn, db: AsyncSession = Depends(get_db)):
    # verify token signature & expiry
    data = decode_token(payload.refresh_token)
    if not data or "sub" not in data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = data["sub"]
    token_hash = hashlib.sha256(payload.refresh_token.encode()).hexdigest()

    q = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.exec(q)
    stored = result.one_or_none()
    if not stored or stored.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")
    if stored.expires_at and stored.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # rotate refresh token: revoke old, create new record
    stored.revoked = True
    new_refresh = create_refresh_token(user_id)
    new_hash = hashlib.sha256(new_refresh.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_rt = RefreshToken(user_id=stored.user_id, token_hash=new_hash, expires_at=expires_at)
    db.add(new_rt)
    await db.commit()

    access = create_access_token(user_id)
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}


class _RevokeIn(SQLModel):
    refresh_token: str | None = None
    revoke_all: bool | None = False


@router.post("/logout")
async def logout(payload: _RevokeIn, db: AsyncSession = Depends(get_db)):
    # revoke a single refresh token or all tokens for the user
    if payload.revoke_all:
        # require refresh_token to identify user
        raise HTTPException(status_code=400, detail="revoke_all requires a refresh_token to identify the user")

    if payload.refresh_token:
        data = decode_token(payload.refresh_token)
        if not data or "sub" not in data:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        token_hash = hashlib.sha256(payload.refresh_token.encode()).hexdigest()
        q = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await db.exec(q)
        stored = result.one_or_none()
        if stored:
            stored.revoked = True
            await db.commit()
        return {"ok": True}

    raise HTTPException(status_code=400, detail="No refresh_token provided to revoke")
