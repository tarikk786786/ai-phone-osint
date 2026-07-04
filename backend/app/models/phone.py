"""PhoneLookup model — stores phone number lookups and their results."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class PhoneLookup(Base, TimestampMixin):
    __tablename__ = "phone_lookups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    phone_number: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    raw_input: Mapped[str] = mapped_column(String(50), nullable=False)

    # Validation results
    is_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    country_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    country_iso: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    country_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    carrier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    line_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    timezones: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Enhanced OSINT data
    formatted_international: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    formatted_national: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    e164: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_spam_risk: Mapped[bool] = mapped_column(Boolean, default=False)
    spam_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Geolocation
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geolocation_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # AI investigation
    ai_report_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    risk_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Raw response cache
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationship
    user: Mapped[Optional["User"]] = relationship(back_populates="lookups")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "phone_number": self.phone_number,
            "raw_input": self.raw_input,
            "is_valid": self.is_valid,
            "country_code": self.country_code,
            "country_iso": self.country_iso,
            "country_name": self.country_name,
            "location": self.location,
            "carrier": self.carrier,
            "line_type": self.line_type,
            "timezones": self.timezones,
            "formatted_international": self.formatted_international,
            "formatted_national": self.formatted_national,
            "e164": self.e164,
            "is_spam_risk": self.is_spam_risk,
            "spam_score": self.spam_score,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "geolocation_source": self.geolocation_source,
            "ai_report_id": self.ai_report_id,
            "risk_score": self.risk_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }



