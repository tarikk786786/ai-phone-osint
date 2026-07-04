"""Location tools endpoint - dedicated mobile location finder tools from GitHub OSINT ecosystem."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_optional_user
from app.models.user import User
from app.services.geolocation_service import geolocation_service, GeoLocation
from app.services.imei_service import imei_lookup_service
from app.services.ip_geolocation_service import ip_geolocation_service
from app.services.wifi_geolocation_service import wifi_geolocation_service
from app.services.phone_validator import phone_validator

router = APIRouter()


# Response Schemas

class LocationResponse(BaseModel):
    success: bool
    data: dict = Field(default_factory=dict)
    sources_used: list[str] = Field(default_factory=list)
    message: str = ""


# 1. Cell Tower Geolocation

@router.get("/cell-tower", response_model=LocationResponse)
async def cell_tower_location(
    mcc: int = Query(..., description="Mobile Country Code (e.g. 310 for US)"),
    mnc: int = Query(..., description="Mobile Network Code (e.g. 260 for T-Mobile)"),
    lac: int = Query(..., description="Location Area Code"),
    cell_id: int = Query(..., description="Cell ID"),
    signal: Optional[int] = Query(None, description="Signal strength in dBm"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Locate a device using cell tower information (MCC/MNC/LAC/CID)."""
    sources_used = []

    result = await geolocation_service.cell_tower_lookup(mcc, mnc, lac, cell_id)
    if result and result.latitude:
        sources_used.append("opencellid")

    if not result or not result.latitude:
        mozilla_result = await geolocation_service.mozilla_location(
            [{"mcc": mcc, "mnc": mnc, "lac": lac, "cid": cell_id, "signal": signal or -80}]
        )
        if mozilla_result and mozilla_result.latitude:
            result = mozilla_result
            sources_used.append("mozilla-location-service")

    if not result or not result.latitude:
        combined = await wifi_geolocation_service.locate_by_cell_tower(mcc, mnc, lac, cell_id)
        if combined and combined.latitude:
            result = GeoLocation()
            result.latitude = combined.latitude
            result.longitude = combined.longitude
            result.source = combined.source
            result.confidence = combined.confidence
            result.accuracy_km = combined.accuracy_km
            sources_used.append("mozilla-wifi")

    if not result or not result.latitude:
        return LocationResponse(
            success=False,
            message="Could not locate cell tower. Ensure MCC/MNC/LAC/CID are correct.",
        )

    return LocationResponse(
        success=True,
        data=result.to_dict(),
        sources_used=sources_used,
        message=f"Cell tower located via {', '.join(sources_used)}",
    )


# 2. IMEI Device Lookup

@router.get("/imei", response_model=LocationResponse)
async def imei_lookup(
    imei: str = Query(..., description="15-digit IMEI number"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Lookup device information by IMEI number."""
    result = await imei_lookup_service.lookup(imei)
    return LocationResponse(
        success=True,
        data=result.to_dict(),
        sources_used=[result.source] if result.source != "local" else [],
        message="IMEI lookup complete" if result.is_valid else "Invalid IMEI number",
    )


# 3. IP Geolocation

@router.get("/ip", response_model=LocationResponse)
async def ip_location(
    ip: str = Query(..., description="IP address to geolocate"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Geolocate an IP address using multiple free APIs."""
    result = await ip_geolocation_service.lookup(ip)
    if not result:
        return LocationResponse(success=False, message="Could not geolocate IP address")
    return LocationResponse(
        success=True,
        data=result.to_dict(),
        sources_used=[result.source],
        message=f"IP geolocated via {result.source}",
    )


# 4. WiFi BSSID Geolocation

@router.get("/wifi", response_model=LocationResponse)
async def wifi_location(
    bssid: str = Query(..., description="WiFi BSSID (MAC address)"),
    signal: Optional[int] = Query(-50, description="Signal strength in dBm"),
    frequency: Optional[int] = Query(2412, description="Frequency in MHz"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Geolocate using a WiFi access point BSSID."""
    result = await wifi_geolocation_service.locate_by_wifi_bssids(
        [{"mac": bssid, "signal": signal, "frequency": frequency}]
    )
    if not result or not result.latitude:
        return LocationResponse(success=False, message="Could not geolocate WiFi access point")
    return LocationResponse(
        success=True,
        data=result.to_dict(),
        sources_used=[result.source],
        message=f"WiFi located via {result.source}",
    )


# 5. Area Code Location

@router.get("/area-code", response_model=LocationResponse)
async def area_code_location(
    phone: str = Query(..., description="Phone number to extract area code from"),
    country: Optional[str] = Query(None, description="ISO country code"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Estimate location from phone area code using built-in database."""
    validation = phone_validator.validate(phone, country)
    national = validation.formatted_national or phone.lstrip("+")
    if country:
        national = national.lstrip("0")

    result = await geolocation_service.area_code_lookup(national)

    if not result and validation.location:
        result = await geolocation_service.geocode_country_region(
            validation.country_iso or "", validation.location
        )

    if not result or not result.latitude:
        return LocationResponse(success=False, message="Could not find location for this area code")

    return LocationResponse(
        success=True,
        data=result.to_dict(),
        sources_used=[result.source],
        message=f"Area code located via {result.source}",
    )


# 6. Multi-Source Aggregated Geolocation

@router.get("/multi-source", response_model=LocationResponse)
async def multi_source_location(
    phone: str = Query(..., description="Phone number"),
    country: Optional[str] = Query(None, description="ISO country code hint"),
    ip_address: Optional[str] = Query(None, description="Associated IP address"),
    mcc: Optional[int] = Query(None, description="Mobile Country Code"),
    mnc: Optional[int] = Query(None, description="Mobile Network Code"),
    lac: Optional[int] = Query(None, description="Location Area Code"),
    cell_id: Optional[int] = Query(None, description="Cell ID"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Aggregate geolocation from 10+ sources for the best accuracy."""
    validation = phone_validator.validate(phone, country)
    national = validation.formatted_national or phone.lstrip("+")

    result = await geolocation_service.multi_source_geolocate(
        phone_number=national,
        country_iso=validation.country_iso or country,
        location_name=validation.location,
        carrier=validation.carrier,
        ip_address=ip_address,
        mcc=mcc,
        mnc=mnc,
        lac=lac,
        cell_id=cell_id,
    )

    sources_used = [s["source"] for s in result.all_sources] if result.all_sources else [result.source]

    return LocationResponse(
        success=True,
        data=result.to_dict(),
        sources_used=sources_used,
        message=f"Aggregated from {len(sources_used)} source(s): {', '.join(sources_used)}",
    )


# 7. Reverse Geocode

@router.get("/reverse-geocode", response_model=LocationResponse)
async def reverse_geocode(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
):
    """Reverse geocode coordinates to a human-readable address using Nominatim."""
    result = await geolocation_service.reverse_geocode(latitude, longitude)
    return LocationResponse(
        success=True,
        data=result.to_dict(),
        sources_used=["nominatim"],
        message="Reverse geocode complete",
    )


# 8. Domain/IP Resolution

@router.get("/resolve-domain", response_model=LocationResponse)
async def resolve_domain(
    domain: str = Query(..., description="Domain name to resolve and geolocate"),
):
    """Resolve a domain to IP and then geolocate it."""
    result = await ip_geolocation_service.resolve_domain(domain)
    if not result:
        return LocationResponse(success=False, message="Could not resolve or geolocate domain")
    return LocationResponse(
        success=True,
        data=result.to_dict(),
        sources_used=[result.source],
        message=f"Domain resolved and geolocated via {result.source}",
    )


# 9. Available Tools List

@router.get("/tools", response_model=LocationResponse)
async def list_location_tools():
    """List all available mobile location finder tools and their capabilities."""
    tools = {
        "cell_tower": {
            "name": "Cell Tower Geolocation",
            "description": "Locate device using MCC/MNC/LAC/CID cell tower data",
            "sources": ["OpenCellID", "Mozilla Location Service"],
            "requires": ["mcc", "mnc", "lac", "cell_id"],
            "accuracy": "100m - 5km",
        },
        "imei_lookup": {
            "name": "IMEI Device Lookup",
            "description": "Identify device make/model/brand by IMEI number",
            "sources": ["IMEI.info API", "IMEI Database"],
            "requires": ["imei"],
            "accuracy": "Device-level",
        },
        "ip_geolocation": {
            "name": "IP Address Geolocation",
            "description": "Geolocate any IP address to city/country level",
            "sources": ["ip-api.com", "ipwho.is", "ipinfo.io"],
            "requires": ["ip"],
            "accuracy": "City-level (1-10km)",
        },
        "wifi_bssid": {
            "name": "WiFi BSSID Geolocation",
            "description": "Locate device via WiFi access point MAC address",
            "sources": ["Mozilla Location Service"],
            "requires": ["bssid"],
            "accuracy": "10m - 100m",
        },
        "area_code": {
            "name": "Area Code Location",
            "description": "Estimate location from phone area code",
            "sources": ["Built-in Area Code Database", "Nominatim"],
            "requires": ["phone"],
            "accuracy": "City-level",
        },
        "multi_source": {
            "name": "Multi-Source Aggregation",
            "description": "Best accuracy by combining 10+ location sources",
            "sources": [
                "Area Code DB", "Nominatim", "OpenCage", "OpenCellID",
                "Mozilla LS", "ip-api.com", "Google Maps", "Carrier Region",
            ],
            "requires": ["phone"],
            "accuracy": "Best available (aggregated)",
        },
        "reverse_geocode": {
            "name": "Reverse Geocoding",
            "description": "Convert coordinates to human-readable address",
            "sources": ["Nominatim (OpenStreetMap)"],
            "requires": ["latitude", "longitude"],
            "accuracy": "Address-level",
        },
        "phone_validation": {
            "name": "Phone Number Validation",
            "description": "Validate and extract metadata from phone numbers",
            "sources": ["Google libphonenumber"],
            "requires": ["phone"],
            "accuracy": "Number-level",
        },
        "osint_scan": {
            "name": "Phone OSINT Scan",
            "description": "Scan 15+ public databases for phone number intelligence",
            "sources": [
                "spamcalls.net", "spamnumber.com", "who-called.me",
                "callersmart.com", "truecaller.com", "shouldianswer.net",
                "tellows.com", "888notes.com", "haveibeenpwned",
                "WhatsApp", "Telegram", "Signal", "Viber",
                "Facebook", "Instagram", "Twitter", "LinkedIn",
            ],
            "requires": ["phone"],
            "accuracy": "Public data only",
        },
        "social_media": {
            "name": "Social Media Detection",
            "description": "Check 10 social platforms for phone number presence",
            "sources": [
                "WhatsApp", "Telegram", "Signal", "Viber",
                "Facebook", "Instagram", "Twitter", "LinkedIn",
                "TikTok", "Snapchat",
            ],
            "requires": ["phone"],
            "accuracy": "Presence detection",
        },
        "spam_detection": {
            "name": "Spam & Fraud Detection",
            "description": "Check 8+ spam databases and score risk level",
            "sources": [
                "spamcalls.net", "spamnumber.com", "who-called.me",
                "callersmart.com", "truecaller.com", "shouldianswer.net",
                "tellows.com", "888notes.com",
            ],
            "requires": ["phone"],
            "accuracy": "Community-sourced",
        },
    }

    return LocationResponse(
        success=True,
        data=tools,
        sources_used=[],
        message=f"{len(tools)} location tools available",
    )
