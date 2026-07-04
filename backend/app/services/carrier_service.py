"""Carrier lookup service — uses multiple sources for carrier detection."""

from __future__ import annotations

from typing import Any, Optional

import aiohttp
from app.core.config import settings


class CarrierInfo:
    """Carrier lookup result."""

    def __init__(self) -> None:
        self.carrier: Optional[str] = None
        self.line_type: Optional[str] = None
        self.is_voip: bool = False
        self.is_prepaid: bool = False
        self.is_ported: bool = False
        self.source: str = "local"
        self.country: Optional[str] = None
        self.network_type: Optional[str] = None
        self.mcc: Optional[int] = None
        self.mnc: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "carrier": self.carrier,
            "line_type": self.line_type,
            "is_voip": self.is_voip,
            "is_prepaid": self.is_prepaid,
            "is_ported": self.is_ported,
            "source": self.source,
            "country": self.country,
            "network_type": self.network_type,
            "mcc": self.mcc,
            "mnc": self.mnc,
        }


class CarrierLookupService:
    """Lookup carrier information from multiple API providers."""

    def __init__(self) -> None:
        self.api_keys = {
            "numverify": settings.NUMVERIFY_API_KEY,
            "abstract": settings.ABSTRACT_API_KEY,
            "ipqualityscore": settings.IPQUALITYSCORE_API_KEY,
        }

    async def lookup(self, phone_number: str, country_iso: Optional[str] = None) -> CarrierInfo:
        """Try multiple APIs in order of preference, return first successful result."""
        result = CarrierInfo()

        # Try Numverify first (if key available)
        if self.api_keys.get("numverify"):
            try:
                result = await self._lookup_numverify(phone_number)
                if result.carrier or result.line_type:
                    result.source = "numverify"
                    return result
            except Exception:
                pass

        # Try Abstract API
        if self.api_keys.get("abstract"):
            try:
                result = await self._lookup_abstract(phone_number)
                if result.carrier or result.line_type:
                    result.source = "abstract"
                    return result
            except Exception:
                pass

        # Try IPQualityScore
        if self.api_keys.get("ipqualityscore"):
            try:
                result = await self._lookup_ipqualityscore(phone_number)
                if result.carrier or result.line_type:
                    result.source = "ipqualityscore"
                    return result
            except Exception:
                pass

        result.source = "unavailable"
        return result

    async def _lookup_numverify(self, phone: str) -> CarrierInfo:
        """Query Numverify API."""
        async with aiohttp.ClientSession() as session:
            params: dict[str, Any] = {
                "access_key": self.api_keys["numverify"],
                "number": phone,
            }
            async with session.get(
                "https://api.apilayer.com/number_verification/validate",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    info = CarrierInfo()
                    info.carrier = data.get("carrier")
                    info.line_type = data.get("line_type")
                    info.country = data.get("country_name")
                    info.is_ported = data.get("ported", False)
                    if data.get("line_type") == "voip":
                        info.is_voip = True
                    return info
        return CarrierInfo()

    async def _lookup_abstract(self, phone: str) -> CarrierInfo:
        """Query Abstract Phone Validation API."""
        async with aiohttp.ClientSession() as session:
            params = {
                "api_key": self.api_keys["abstract"],
                "phone": phone,
            }
            async with session.get(
                "https://phonevalidation.abstractapi.com/v1/",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    info = CarrierInfo()
                    info.carrier = data.get("carrier", {}).get("name")
                    info.line_type = data.get("line_type")
                    info.country = data.get("country", {}).get("name")
                    info.network_type = data.get("carrier", {}).get("network_type")
                    return info
        return CarrierInfo()

    async def _lookup_ipqualityscore(self, phone: str) -> CarrierInfo:
        """Query IPQualityScore API."""
        if not self.api_keys.get("ipqualityscore"):
            return CarrierInfo()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://ipqualityscore.com/api/json/phone/{self.api_keys['ipqualityscore']}/{phone}",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        info = CarrierInfo()
                        info.carrier = data.get("carrier")
                        info.line_type = data.get("line_type", data.get("type"))
                        info.is_voip = data.get("voip", False)
                        info.is_prepaid = data.get("prepaid", False)
                        info.is_ported = data.get("ported", False)
                        info.country = data.get("country")
                        return info
        return CarrierInfo()


carrier_lookup_service = CarrierLookupService()
