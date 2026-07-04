"""Location tools endpoint - dedicated mobile location finder tools from GitHub OSINT ecosystem."""

from __future__ import annotations

import asyncio
import re
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
from app.services.osint_service import osint_service

router = APIRouter()


class LocationResponse(BaseModel):
    success: bool
    data: dict = Field(default_factory=dict)
    sources_used: list[str] = Field(default_factory=list)
    message: str = ""


class UniversalSearchResponse(BaseModel):
    success: bool
    input_type: str
    detected_value: str
    results: dict = Field(default_factory=dict)
    sources_used: list[str] = Field(default_factory=list)
    tools_run: list[str] = Field(default_factory=list)
    message: str = ""


# ── Input Type Detection ────────────────────────────────

def detect_input_type(value: str) -> tuple[str, str]:
    """
    Detect the type of input and return (type, normalized_value).
    
    Returns:
        (type, normalized_value) where type is one of:
        - "phone" - Phone number
        - "imei" - IMEI number (15 digits)
        - "ip" - IPv4 or IPv6 address
        - "wifi_bssid" - WiFi MAC address (AA:BB:CC:DD:EE:FF)
        - "domain" - Domain name (example.com)
        - "coordinates" - Latitude,Longitude
        - "unknown" - Cannot determine type
    """
    value = value.strip()
    
    # Check for coordinates (lat,lon)
    coord_match = re.match(r'^(-?\d+\.?\d*)\s*[,]\s*(-?\d+\.?\d*)$', value)
    if coord_match:
        lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return "coordinates", value
    
    # Check for IP address (IPv4 or IPv6)
    ipv4_match = re.match(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', value)
    if ipv4_match:
        octets = [int(o) for o in ipv4_match.groups()]
        if all(0 <= o <= 255 for o in octets):
            return "ip", value
    
    # IPv6 check
    if ':' in value and re.match(r'^[0-9a-fA-F:]+$', value):
        return "ip", value
    
    # Check for WiFi BSSID (MAC address format)
    bssid_match = re.match(r'^([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}$', value)
    if bssid_match:
        return "wifi_bssid", value.upper()
    
    # Check for IMEI (15 digits, possibly with dashes)
    digits_only = value.replace('-', '').replace(' ', '')
    if re.match(r'^\d{15}$', digits_only):
        # Could be IMEI or phone number - check if it looks like a phone
        if value.startswith('+') or value.startswith('00'):
            return "phone", value
        # Check IMEI Luhn validity
        if imei_lookup_service.validate_imei(digits_only):
            return "imei", digits_only
        # Default to phone if starts with common country codes
        if digits_only.startswith(('1', '44', '91', '86', '81', '82', '33', '49', '39', '34', '55')):
            return "phone", value
        return "phone", value
    
    # Check for phone number (with + prefix or common patterns)
    if value.startswith('+') or re.match(r'^\d{7,15}$', digits_only):
        return "phone", value
    
    # Check for domain name
    domain_match = re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', value)
    if domain_match:
        return "domain", value.lower()
    
    # If it has dots but isn't IP or domain, might be a subdomain
    if '.' in value and not value.replace('.', '').isdigit():
        return "domain", value.lower()
    
    return "unknown", value


# ── 1. Universal Search ────────────────────────────────

@router.get("/universal-search", response_model=UniversalSearchResponse)
async def universal_search(
    q: str = Query(..., description="Any input: phone, IMEI, IP, WiFi BSSID, domain, or coordinates"),
    country: Optional[str] = Query(None, description="ISO country code hint for phone numbers"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """
    Universal search tool - accepts ANY input and runs ALL relevant tools in parallel.
    
    Auto-detects input type:
    - Phone number -> runs phone validation, carrier lookup, OSINT scan, geolocation
    - IMEI number -> runs IMEI device lookup, validation
    - IP address -> runs IP geolocation from 3 sources
    - WiFi BSSID -> runs WiFi BSSID geolocation
    - Domain name -> runs domain resolution + IP geolocation
    - Coordinates -> runs reverse geocoding
    
    All detected tools run in parallel for maximum speed.
    """
    input_type, normalized_value = detect_input_type(q)
    results: dict[str, Any] = {}
    sources_used: list[str] = []
    tools_run: list[str] = []
    
    if input_type == "unknown":
        return UniversalSearchResponse(
            success=False,
            input_type=input_type,
            detected_value=normalized_value,
            results={},
            sources_used=[],
            tools_run=[],
            message="Could not detect input type. Please enter a phone number, IMEI, IP address, WiFi BSSID, domain, or coordinates.",
        )
    
    # ── Phone Number ───────────────────────────────────
    if input_type == "phone":
        async def run_phone_validation():
            return phone_validator.validate(normalized_value, country)
        
        async def run_osint_scan():
            validation = phone_validator.validate(normalized_value, country)
            e164 = validation.e164 or normalized_value
            return await osint_service.investigate(e164, e164)
        
        async def run_geolocation():
            validation = phone_validator.validate(normalized_value, country)
            return await geolocation_service.multi_source_geolocate(
                phone_number=validation.formatted_national or normalized_value,
                country_iso=validation.country_iso or country,
                location_name=validation.location,
                carrier=validation.carrier,
            )
        
        async def run_area_code():
            validation = phone_validator.validate(normalized_value, country)
            national = validation.formatted_national or normalized_value.lstrip('+')
            return await geolocation_service.area_code_lookup(national)
        
        tasks = {
            "phone_validation": run_phone_validation(),
            "osint_scan": run_osint_scan(),
            "geolocation": run_geolocation(),
            "area_code": run_area_code(),
        }
        
        task_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for (tool_name, _), result in zip(tasks.items(), task_results):
            if not isinstance(result, Exception) and result is not None:
                if hasattr(result, 'to_dict'):
                    results[tool_name] = result.to_dict()
                else:
                    results[tool_name] = result
                tools_run.append(tool_name)
        
        # Extract useful data
        validation = results.get("phone_validation", {})
        results["summary"] = {
            "valid": validation.get("is_valid"),
            "country": validation.get("country_name"),
            "country_iso": validation.get("country_iso"),
            "carrier": validation.get("carrier"),
            "location": validation.get("location"),
            "line_type": validation.get("line_type"),
            "e164": validation.get("e164"),
        }
        
        sources_used = ["libphonenumber", "osint-8+sources", "multi-source-geo", "area-code-db"]
    
    # ── IMEI Number ────────────────────────────────────
    elif input_type == "imei":
        async def run_imei_lookup():
            return await imei_lookup_service.lookup(normalized_value)
        
        result = await run_imei_lookup()
        if result:
            results["imei_lookup"] = result.to_dict()
            tools_run.append("imei_lookup")
            results["summary"] = {
                "valid": result.is_valid,
                "brand": result.brand,
                "manufacturer": result.manufacturer,
                "model": result.model,
                "device_name": result.device_name,
                "device_type": result.device_type,
                "os": result.os,
                "tac": result.tac,
                "is_stolen": result.is_stolen,
                "blacklisted": result.blacklisted,
            }
            sources_used = ["imei-api", "luhn-validation"]
    
    # ── IP Address ─────────────────────────────────────
    elif input_type == "ip":
        async def run_ip_geolocation():
            return await ip_geolocation_service.lookup(normalized_value)
        
        async def run_reverse_geocode():
            geo = await ip_geolocation_service.lookup(normalized_value)
            if geo and geo.latitude:
                return await geolocation_service.reverse_geocode(geo.latitude, geo.longitude)
            return None
        
        tasks = {
            "ip_geolocation": run_ip_geolocation(),
            "reverse_geocode": run_reverse_geocode(),
        }
        
        task_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for (tool_name, _), result in zip(tasks.items(), task_results):
            if not isinstance(result, Exception) and result is not None:
                if hasattr(result, 'to_dict'):
                    results[tool_name] = result.to_dict()
                else:
                    results[tool_name] = result
                tools_run.append(tool_name)
        
        ip_data = results.get("ip_geolocation", {})
        results["summary"] = {
            "ip": ip_data.get("ip"),
            "country": ip_data.get("country"),
            "city": ip_data.get("city"),
            "region": ip_data.get("region"),
            "isp": ip_data.get("isp"),
            "org": ip_data.get("org"),
            "proxy": ip_data.get("proxy"),
            "hosting": ip_data.get("hosting"),
        }
        sources_used = ["ip-api.com", "ipwho.is", "ipinfo.io", "nominatim"]
    
    # ── WiFi BSSID ─────────────────────────────────────
    elif input_type == "wifi_bssid":
        async def run_wifi_geolocation():
            return await wifi_geolocation_service.locate_by_wifi_bssids(
                [{"mac": normalized_value, "signal": -50, "frequency": 2412}]
            )
        
        result = await run_wifi_geolocation()
        if result and result.latitude:
            results["wifi_geolocation"] = result.to_dict()
            tools_run.append("wifi_geolocation")
            
            # Also reverse geocode for address
            reverse = await geolocation_service.reverse_geocode(result.latitude, result.longitude)
            if reverse:
                results["reverse_geocode"] = reverse.to_dict()
                tools_run.append("reverse_geocode")
            
            results["summary"] = {
                "latitude": result.latitude,
                "longitude": result.longitude,
                "source": result.source,
                "accuracy_km": result.accuracy_km,
            }
            sources_used = ["mozilla-location-service", "nominatim"]
        else:
            results["summary"] = {"error": "Could not geolocate WiFi BSSID"}
    
    # ── Domain Name ────────────────────────────────────
    elif input_type == "domain":
        async def run_domain_resolution():
            return await ip_geolocation_service.resolve_domain(normalized_value)
        
        result = await run_domain_resolution()
        if result:
            results["domain_resolution"] = result.to_dict()
            tools_run.append("domain_resolution")
            
            # Also reverse geocode if we got coordinates
            if result.latitude:
                reverse = await geolocation_service.reverse_geocode(result.latitude, result.longitude)
                if reverse:
                    results["reverse_geocode"] = reverse.to_dict()
                    tools_run.append("reverse_geocode")
            
            results["summary"] = {
                "domain": normalized_value,
                "resolved_ip": result.ip,
                "country": result.country,
                "city": result.city,
                "isp": result.isp,
            }
            sources_used = ["dns-resolution", "ip-api.com", "ipwho.is", "ipinfo.io"]
        else:
            results["summary"] = {"error": "Could not resolve domain"}
    
    # ── Coordinates ────────────────────────────────────
    elif input_type == "coordinates":
        coord_match = re.match(r'^(-?\d+\.?\d*)\s*[,]\s*(-?\d+\.?\d*)$', normalized_value)
        if coord_match:
            lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
            
            result = await geolocation_service.reverse_geocode(lat, lon)
            if result:
                results["reverse_geocode"] = result.to_dict()
                tools_run.append("reverse_geocode")
                results["summary"] = {
                    "latitude": lat,
                    "longitude": lon,
                    "address": result.address,
                    "city": result.city,
                    "state": result.state,
                    "country": result.country,
                }
                sources_used = ["nominatim"]
    
    return UniversalSearchResponse(
        success=True,
        input_type=input_type,
        detected_value=normalized_value,
        results=results,
        sources_used=sources_used,
        tools_run=tools_run,
        message=f"Universal search complete. Detected {input_type} and ran {len(tools_run)} tool(s).",
    )


# ── 2. Cell Tower Geolocation ──────────────────────────

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


# ── 3. IMEI Device Lookup ─────────────────────────────

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


# ── 4. IP Geolocation ─────────────────────────────────

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


# ── 5. WiFi BSSID Geolocation ─────────────────────────

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


# ── 6. Area Code Location ──────────────────────────────

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


# ── 7. Multi-Source Aggregated Geolocation ─────────────

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


# ── 8. Reverse Geocode ─────────────────────────────────

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


# ── 9. Domain/IP Resolution ────────────────────────────

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


# ── 10. Available Tools List ───────────────────────────

@router.get("/tools", response_model=LocationResponse)
async def list_location_tools():
    """List all available mobile location finder tools and their capabilities."""
    tools = {
        "universal_search": {
            "name": "Universal Search",
            "description": "Auto-detect input type and run ALL relevant tools in parallel",
            "sources": ["All sources combined"],
            "requires": ["q (any input)"],
            "accuracy": "Best available",
        },
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
