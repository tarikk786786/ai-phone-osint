"""User model — authentication, roles, API keys."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import hash_password, verify_password
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.phone import PhoneLookup
    from app.models.audit_log import AuditLog


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Roles & permissions
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), default="user")  # user | admin | analyst

    # Usage tracking
    api_calls_today: Mapped[int] = mapped_column(default=0)
    api_call_limit: Mapped[int] = mapped_column(default=100)

    # Relationships
    lookups: Mapped[list["PhoneLookup"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.hashed_password = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "api_calls_today": self.api_calls_today,
            "api_call_limit": self.api_call_limit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
