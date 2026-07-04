"""Geolocation service — cell tower, reverse geocoding, maps."""

from __future__ import annotations

from typing import Any, Optional

import aiohttp
from app.core.config import settings


class GeoLocation:
    """Geolocation result with confidence level."""

    def __init__(self) -> None:
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.address: Optional[str] = None
        self.city: Optional[str] = None
        self.state: Optional[str] = None
        self.country: Optional[str] = None
        self.postal_code: Optional[str] = None
        self.source: str = "unknown"
        self.confidence: str = "estimated"  # verified | estimated | public
        self.accuracy_km: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "source": self.source,
            "confidence": self.confidence,
            "accuracy_km": self.accuracy_km,
        }


class GeolocationService:
    """Geolocation via OpenCellID, Nominatim, and other public sources."""

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
    ) -> GeoLocation:
        """Reverse geocode coordinates to an address using Nominatim."""
        result = GeoLocation()
        result.latitude = latitude
        result.longitude = longitude
        result.source = "nominatim"
        result.confidence = "verified"

        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": f"PhoneOSINT/1.0 (research project; contact@example.com)"
            }
            async with session.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "format": "json",
                    "addressdetails": 1,
                },
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "address" in data:
                        addr = data["address"]
                        result.address = data.get("display_name")
                        result.city = (
                            addr.get("city")
                            or addr.get("town")
                            or addr.get("village")
                            or addr.get("hamlet")
                        )
                        result.state = addr.get("state")
                        result.country = addr.get("country")
                        result.postal_code = addr.get("postcode")

        return result

    async def cell_tower_lookup(
        self,
        mcc: int,
        mnc: int,
        lac: int,
        cell_id: int,
    ) -> Optional[GeoLocation]:
        """Look up cell tower location from OpenCellID."""
        if not settings.OPENCELLID_API_KEY:
            return None

        result = GeoLocation()
        result.source = "opencellid"
        result.confidence = "public"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://opencellid.org/cell/get",
                params={
                    "key": settings.OPENCELLID_API_KEY,
                    "mcc": mcc,
                    "mnc": mnc,
                    "lac": lac,
                    "cellid": cell_id,
                    "format": "json",
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "lat" in data and "lon" in data:
                        result.latitude = float(data["lat"])
                        result.longitude = float(data["lon"])
                        result.accuracy_km = data.get("accuracy")
                        return result

        return None

    async def geocode_country_region(
        self, country_iso: str, location_name: Optional[str] = None
    ) -> Optional[GeoLocation]:
        """Get approximate coordinates for a country/region using Nominatim."""
        query = location_name or country_iso

        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": f"PhoneOSINT/1.0 (research project; contact@example.com)"
            }
            async with session.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1,
                },
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        result = GeoLocation()
                        result.latitude = float(data[0]["lat"])
                        result.longitude = float(data[0]["lon"])
                        result.address = data[0].get("display_name")
                        result.source = "nominatim"
                        result.confidence = "estimated"
                        return result

        return None


geolocation_service = GeolocationService()
