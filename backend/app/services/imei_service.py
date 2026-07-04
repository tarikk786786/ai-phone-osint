"""IMEI lookup service — validate, identify device make/model, and check blacklist status."""

from __future__ import annotations

from typing import Any, Optional

import aiohttp


class IMEIResult:
    """IMEI lookup result with device information."""

    def __init__(self) -> None:
        self.imei: str = ""
        self.is_valid: bool = False
        self.device_name: Optional[str] = None
        self.manufacturer: Optional[str] = None
        self.brand: Optional[str] = None
        self.model: Optional[str] = None
        self.device_type: Optional[str] = None
        self.os: Optional[str] = None
        self.sim_count: Optional[int] = None
        self.release_date: Optional[str] = None
        self.country: Optional[str] = None
        self.is_stolen: Optional[bool] = None
        self.blacklisted: Optional[bool] = None
        self.tac: Optional[str] = None
        self.source: str = "local"
        self.raw_data: dict[str, Any] = {}

    def to_dict(self) -> dict:
        return {
            "imei": self.imei,
            "is_valid": self.is_valid,
            "device_name": self.device_name,
            "manufacturer": self.manufacturer,
            "brand": self.brand,
            "model": self.model,
            "device_type": self.device_type,
            "os": self.os,
            "sim_count": self.sim_count,
            "release_date": self.release_date,
            "country": self.country,
            "is_stolen": self.is_stolen,
            "blacklisted": self.blacklisted,
            "tac": self.tac,
            "source": self.source,
            "raw_data": self.raw_data,
        }


class IMEILookupService:
    """Validate IMEI and lookup device information from multiple sources."""

    @staticmethod
    def validate_imei(imei: str) -> bool:
        """Validate IMEI using Luhn algorithm (ISO/IEC 7812)."""
        imei_clean = imei.replace("-", "").replace(" ", "").strip()
        if len(imei_clean) != 15 or not imei_clean.isdigit():
            return False

        total = 0
        for i, digit in enumerate(reversed(imei_clean)):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0

    @staticmethod
    def extract_tac(imei: str) -> str:
        """Extract Type Allocation Code (first 8 digits) from IMEI."""
        return imei.replace("-", "").replace(" ", "")[:8]

    async def lookup(self, imei: str) -> IMEIResult:
        """Validate IMEI and gather device information from multiple sources."""
        result = IMEIResult()
        result.imei = imei.replace("-", "").replace(" ", "").strip()
        result.is_valid = self.validate_imei(result.imei)

        if not result.is_valid:
            return result

        result.tac = self.extract_tac(result.imei)

        # Try multiple sources in parallel
        sources = [
            self._lookup_imei_info_api(result.imei),
            self._lookup_imeidb(result.imei),
        ]

        for source_coro in sources:
            try:
                source_data = await source_coro
                if source_data:
                    self._merge_device_data(result, source_data)
                    break
            except Exception:
                continue

        return result

    async def _lookup_imei_info_api(self, imei: str) -> Optional[dict]:
        """Lookup device info from imei.info-style API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.imeicheck.com/standalone/check?imei={imei}",
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={"User-Agent": "PhoneOSINT/1.0"},
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            return data
        except Exception:
            pass
        return None

    async def _lookup_imeidb(self, imei: str) -> Optional[dict]:
        """Lookup device info from imeidb-style sources."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://imeidb.io/api/v1/lookup/{imei}",
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={"User-Agent": "PhoneOSINT/1.0"},
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            return data
        except Exception:
            pass
        return None

    def _merge_device_data(self, result: IMEIResult, data: dict) -> None:
        """Merge device data from various API formats into result."""
        result.source = "api"
        result.raw_data = data

        result.device_name = (
            data.get("device_name")
            or data.get("deviceName")
            or data.get("name")
            or data.get("marketing_name")
        )
        result.manufacturer = (
            data.get("manufacturer")
            or data.get("brand")
            or data.get("oem")
        )
        result.brand = data.get("brand") or data.get("manufacturer")
        result.model = data.get("model") or data.get("model_number")
        result.device_type = (
            data.get("type")
            or data.get("device_type")
            or data.get("deviceType")
        )
        result.os = data.get("os") or data.get("operating_system")
        result.release_date = (
            data.get("release_date")
            or data.get("releaseDate")
            or data.get("released")
        )
        result.country = data.get("country") or data.get("origin")
        result.is_stolen = data.get("is_stolen") or data.get("stolen")
        result.blacklisted = data.get("blacklisted") or data.get("is_blacklisted")


imei_lookup_service = IMEILookupService()
