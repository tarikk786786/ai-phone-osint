"""FastAPI dependency injection — auth, DB sessions, rate limiting."""

from __future__ import annotations

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_postgres_session, get_redis
from app.core.security import decode_token
from app.models.user import User
from app.models.api_key import ApiKey

security_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_postgres_session():
        yield session


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Authenticate user via JWT or API key."""
    if credentials:
        payload = decode_token(credentials.credentials)
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            if user_id:
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                if user and user.is_active:
                    return user

    if api_key:
        # Hash the provided key and look it up
        import hashlib
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        result = await db.execute(
            select(ApiKey).where(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True,
            )
        )
        api_key_obj = result.scalar_one_or_none()
        if api_key_obj:
            result = await db.execute(select(User).where(User.id == api_key_obj.user_id))
            user = result.scalar_one_or_none()
            if user and user.is_active:
                return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Authenticate if possible, but don't raise if not authenticated."""
    try:
        return await get_current_user(credentials, api_key, db)
    except HTTPException:
        return None


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user
