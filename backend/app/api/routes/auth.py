"""Authentication endpoints — register, login, token refresh."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
)
from app.models.user import User
from app.models.api_key import ApiKey

router = APIRouter()


# ── Schemas ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class APIKeyResponse(BaseModel):
    api_key: str
    key_prefix: str
    name: str


# ── Endpoints ───────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Register a new user account."""
    # Check existing
    existing = await db.execute(
        select(User).where((User.email == request.email) | (User.username == request.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        )

    user = User(email=request.email, username=request.username)
    user.set_password(request.password)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
        user=user.to_dict(),
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate and receive tokens."""
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    user = result.scalar_one_or_none()

    if not user or not user.check_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated",
        )

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
        user=user.to_dict(),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Refresh an access token using a refresh token."""
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
        user=user.to_dict(),
    )


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)) -> dict:
    """Get current user profile."""
    return user.to_dict()


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    name: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> APIKeyResponse:
    """Generate a new API key."""
    import hashlib
    key = generate_api_key()
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    key_prefix = key[:8]

    api_key_obj = ApiKey(
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=name,
    )
    db.add(api_key_obj)
    await db.commit()

    return APIKeyResponse(api_key=key, key_prefix=key_prefix, name=name)
