"""Admin endpoints — user management, usage statistics, audit logs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models.user import User
from app.models.phone import PhoneLookup
from app.models.audit_log import AuditLog

router = APIRouter()


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all users (admin only)."""
    offset = (page - 1) * per_page
    result = await db.execute(select(User).offset(offset).limit(per_page))
    users = result.scalars().all()
    return {"success": True, "data": [u.to_dict() for u in users], "page": page}


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get system-wide usage statistics."""
    # Total users
    user_count = await db.scalar(select(func.count(User.id)))

    # Total lookups
    lookup_count = await db.scalar(select(func.count(PhoneLookup.id)))

    # Lookups today
    from datetime import datetime, timezone, timedelta
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_lookups = await db.scalar(
        select(func.count(PhoneLookup.id)).where(PhoneLookup.created_at >= today_start)
    )

    # Top users
    top_users_result = await db.execute(
        select(
            User.username,
            func.count(PhoneLookup.id).label("lookup_count"),
        )
        .join(PhoneLookup, PhoneLookup.user_id == User.id)
        .group_by(User.username)
        .order_by(desc("lookup_count"))
        .limit(10)
    )
    top_users = [{"username": row[0], "lookups": row[1]} for row in top_users_result]

    return {
        "success": True,
        "data": {
            "total_users": user_count,
            "total_lookups": lookup_count,
            "lookups_today": today_lookups,
            "top_users": top_users,
        },
    }


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update a user's role."""
    if role not in ("user", "admin", "analyst"):
        raise HTTPException(status_code=400, detail="Invalid role")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    await db.commit()
    return {"success": True, "data": user.to_dict()}
