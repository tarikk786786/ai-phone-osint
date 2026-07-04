"""Phone lookup endpoint — the core intelligence API."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, get_optional_user
from app.core.database import get_redis
from app.models.user import User
from app.models.phone import PhoneLookup
from app.services.phone_validator import phone_validator
from app.services.carrier_service import carrier_lookup_service
from app.services.geolocation_service import geolocation_service
from app.services.osint_service import osint_service
from app.services.ai_service import ai_service
from app.services.export_service import export_service

router = APIRouter()


# ── Response Schemas ────────────────────────────────────

class PhoneLookupResponse(BaseModel):
    success: bool
    data: dict = Field(default_factory=dict)
    osint: Optional[dict] = None
    geolocation: Optional[dict] = None
    ai_report: Optional[dict] = None
    lookup_id: Optional[str] = None
    cached: bool = False
    message: str = ""


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


# ── Lookup Endpoints ────────────────────────────────────

@router.get("/validate", response_model=PhoneLookupResponse)
async def validate_phone(
    phone: str = Query(..., description="Phone number to validate"),
    country: Optional[str] = Query(None, description="ISO country code hint (e.g., US, IN)"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """
    Validate and parse a phone number using libphonenumber.

    Returns: validity, country, carrier, line type, timezones, formatting.
    """
    result = phone_validator.validate(phone, country)

    if not result.is_valid and not result.is_possible:
        return PhoneLookupResponse(
            success=False,
            message="Invalid phone number — could not be parsed or recognized",
        )

    return PhoneLookupResponse(
        success=True,
        data=result.to_dict(),
        message="Phone validation complete",
    )


@router.get("/lookup", response_model=PhoneLookupResponse)
async def full_phone_lookup(
    phone: str = Query(..., description="Phone number for full intelligence lookup"),
    country: Optional[str] = Query(None, description="ISO country code hint"),
    include_osint: bool = Query(True, description="Include OSINT gathering"),
    include_geolocation: bool = Query(True, description="Include geolocation estimate"),
    include_ai: bool = Query(True, description="Include AI investigation report"),
    ai_provider: str = Query("auto", description="AI provider: auto, openai, gemini, deepseek, qwen, ollama"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """
    Full phone number intelligence lookup.

    Combines:
    - Phone validation (libphonenumber)
    - Carrier lookup (multiple API sources)
    - Geolocation estimate (public databases only — NOT GPS)
    - OSINT intelligence (public sources)
    - AI investigation report (if API keys configured)
    """
    # Step 1: Validate phone
    validation = phone_validator.validate(phone, country)
    if not validation.is_valid:
        return PhoneLookupResponse(
            success=False,
            message="Invalid phone number — could not be validated",
        )

    phone_data = validation.to_dict()
    e164 = phone_data.get("e164", phone)
    country_iso = phone_data.get("country_iso")

    # Step 2: Carrier lookup
    carrier_info = await carrier_lookup_service.lookup(e164, country_iso)
    phone_data["carrier_extended"] = carrier_info.to_dict()
    if carrier_info.carrier:
        phone_data["carrier"] = carrier_info.carrier
    if carrier_info.line_type:
        phone_data["line_type"] = carrier_info.line_type

    # Step 3: OSINT (optional)
    osint_data = {}
    if include_osint:
        osint_result = await osint_service.investigate(e164, e164)
        osint_data = osint_result.to_dict()
        phone_data["spam_risk"] = osint_data.get("spam_risk")
        phone_data["spam_score"] = osint_data.get("spam_score")

    # Step 4: Geolocation (optional)
    geo_data = None
    if include_geolocation and phone_data.get("location"):
        geo_result = await geolocation_service.geocode_country_region(
            country_iso or "", phone_data.get("location")
        )
        if geo_result:
            geo_data = geo_result.to_dict()
            phone_data["latitude"] = geo_data.get("latitude")
            phone_data["longitude"] = geo_data.get("longitude")
            phone_data["geolocation_source"] = geo_data.get("source")

    # Step 5: AI Report (optional)
    ai_report = None
    if include_ai:
        ai_report_obj = await ai_service.generate_report(
            phone_data, osint_data, geo_data, preferred_provider=ai_provider
        )
        ai_report = ai_report_obj.to_dict()
        phone_data["risk_score"] = ai_report.get("risk_assessment", {}).get("score")
        phone_data["ai_report_id"] = ai_report.get("model_used", "")

    # Step 6: Store to DB (if authenticated)
    lookup_id = None
    if user:
        lookup = PhoneLookup(
            user_id=user.id,
            phone_number=e164,
            raw_input=phone,
            is_valid=validation.is_valid,
            country_code=validation.country_code,
            country_iso=validation.country_iso,
            country_name=validation.country_name,
            location=validation.location,
            carrier=validation.carrier or (carrier_info.carrier if carrier_info else None),
            line_type=validation.line_type or (carrier_info.line_type if carrier_info else None),
            timezones=validation.timezones,
            formatted_international=validation.formatted_international,
            formatted_national=validation.formatted_national,
            e164=e164,
            is_spam_risk=osint_data.get("spam_risk", False),
            spam_score=osint_data.get("spam_score"),
            latitude=phone_data.get("latitude"),
            longitude=phone_data.get("longitude"),
            geolocation_source=phone_data.get("geolocation_source"),
            risk_score=phone_data.get("risk_score"),
            raw_data=phone_data,
        )
        db.add(lookup)
        await db.commit()
        lookup_id = str(lookup.id)

    return PhoneLookupResponse(
        success=True,
        data=phone_data,
        osint=osint_data if include_osint else None,
        geolocation=geo_data,
        ai_report=ai_report,
        lookup_id=lookup_id,
        message="Phone intelligence lookup complete",
    )


@router.get("/history")
async def get_lookup_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get phone lookup history for the authenticated user."""
    from sqlalchemy import select, desc

    result = await db.execute(
        select(PhoneLookup)
        .where(PhoneLookup.user_id == user.id)
        .order_by(desc(PhoneLookup.created_at))
        .offset(offset)
        .limit(limit)
    )
    lookups = result.scalars().all()
    return {
        "success": True,
        "data": [l.to_dict() for l in lookups],
        "total": len(lookups),
    }


@router.get("/{lookup_id}")
async def get_lookup_by_id(
    lookup_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a specific phone lookup by ID."""
    result = await db.execute(
        select(PhoneLookup).where(
            PhoneLookup.id == lookup_id,
            PhoneLookup.user_id == user.id,
        )
    )
    lookup = result.scalar_one_or_none()
    if not lookup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lookup not found")
    return {"success": True, "data": lookup.to_dict()}
