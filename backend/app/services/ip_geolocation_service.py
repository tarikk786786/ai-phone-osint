"""IP geolocation service - locate devices/IPs using multiple free geolocation APIs."""

from __future__ import annotations

import asyncio
import socket
from typing import Any, Optional

import aiohttp


class IPGeoResult:
    """IP geolocation result with multi-source confidence."""

    def __init__(self) -> None:
        self.ip: str = ""
        self.country: Optional[str] = None
        self.country_code: Optional[str] = None
        self.region: Optional[str] = None
        self.city: Optional[str] = None
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.postal_code: Optional[str] = None
        self.timezone: Optional[str] = None
        self.isp: Optional[str] = None
        self.org: Optional[str] = None
        self.as_number: Optional[str] = None
        self.hosting: Optional[bool] = None
        self.proxy: Optional[bool] = None
        self.vpn: Optional[bool] = None
        self.source: str = "unknown"
        self.accuracy_km: Optional[float] = None
        self.raw_data: dict[str, Any] = {}

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "country": self.country,
            "country_code": self.country_code,
            "region": self.region,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "postal_code": self.postal_code,
            "timezone": self.timezone,
            "isp": self.isp,
            "org": self.org,
            "as_number": self.as_number,
            "hosting": self.hosting,
            "proxy": self.proxy,
            "vpn": self.vpn,
            "source": self.source,
            "accuracy_km": self.accuracy_km,
        }


class IPGeolocationService:
    """Resolve IP addresses to geographic locations using multiple free APIs."""

    async def lookup(self, ip: str) -> Optional[IPGeoResult]:
        """Try multiple IP geolocation APIs in parallel, return first success."""

        async def try_api(func, ip_val):
            try:
                return await func(ip_val)
            except Exception:
                return None

        results = await asyncio.gather(
            try_api(self._lookup_ipapi, ip),
            try_api(self._lookup_ipwhois, ip),
            try_api(self._lookup_ipinfo, ip),
        )

        for result in results:
            if result and result.latitude is not None:
                return result

        return None

    async def _lookup_ipapi(self, ip: str) -> Optional[IPGeoResult]:
        """Use ip-api.com (free, no key required, 45 req/min)."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,hosting,proxy"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status") == "success":
                        result = IPGeoResult()
                        result.ip = ip
                        result.country = data.get("country")
                        result.country_code = data.get("countryCode")
                        result.region = data.get("regionName")
                        result.city = data.get("city")
                        result.latitude = data.get("lat")
                        result.longitude = data.get("lon")
                        result.postal_code = data.get("zip")
                        result.timezone = data.get("timezone")
                        result.isp = data.get("isp")
                        result.org = data.get("org")
                        result.as_number = data.get("as")
                        result.hosting = data.get("hosting")
                        result.proxy = data.get("proxy")
                        result.source = "ip-api.com"
                        result.accuracy_km = 5.0
                        result.raw_data = data
                        return result
        return None

    async def _lookup_ipwhois(self, ip: str) -> Optional[IPGeoResult]:
        """Use ipwho.is (free, no key required)."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://ipwho.is/{ip}",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("success"):
                        result = IPGeoResult()
                        result.ip = ip
                        result.country = data.get("country")
                        result.country_code = data.get("country_code")
                        result.region = data.get("region")
                        result.city = data.get("city")
                        result.latitude = data.get("latitude")
                        result.longitude = data.get("longitude")
                        result.postal_code = data.get("postal")
                        result.timezone = data.get("timezone", {}).get("id")
                        result.isp = data.get("connection", {}).get("isp")
                        result.org = data.get("connection", {}).get("org")
                        result.as_number = data.get("connection", {}).get("asn")
                        result.source = "ipwho.is"
                        result.accuracy_km = 10.0
                        result.raw_data = data
                        return result
        return None

    async def _lookup_ipinfo(self, ip: str) -> Optional[IPGeoResult]:
        """Use ipinfo.io (free tier, 50k req/month)."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://ipinfo.io/{ip}/json",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "loc" in data:
                        lat, lon = data["loc"].split(",")
                        result = IPGeoResult()
                        result.ip = ip
                        result.country = data.get("country")
                        result.region = data.get("region")
                        result.city = data.get("city")
                        result.latitude = float(lat)
                        result.longitude = float(lon)
                        result.postal_code = data.get("postal")
                        result.timezone = data.get("timezone")
                        result.isp = data.get("org")
                        result.as_number = data.get("org")
                        result.source = "ipinfo.io"
                        result.accuracy_km = 10.0
                        result.raw_data = data
                        return result
        return None

    async def resolve_domain(self, domain: str) -> Optional[IPGeoResult]:
        """Resolve a domain to IP and then geolocate it (non-blocking)."""
        try:
            loop = asyncio.get_event_loop()
            ip = await loop.run_in_executor(None, socket.gethostbyname, domain)
            return await self.lookup(ip)
        except (socket.gaierror, OSError):
            return None


ip_geolocation_service = IPGeolocationService()
