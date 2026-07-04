"""Geolocation service — multi-source aggregation with 10+ location methods."""

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
        self.all_sources: list[dict[str, Any]] = []

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
            "all_sources": self.all_sources,
        }


class GeolocationService:
    """Geolocation via 10+ public sources with multi-source aggregation."""

    # ── 1. Nominatim (OpenStreetMap) ────────────────────

    async def reverse_geocode(
        self, latitude: float, longitude: float
    ) -> GeoLocation:
        """Reverse geocode coordinates to an address using Nominatim."""
        result = GeoLocation()
        result.latitude = latitude
        result.longitude = longitude
        result.source = "nominatim"
        result.confidence = "verified"

        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "PhoneOSINT/1.0 (research project)"}
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

    # ── 2. OpenCellID Cell Tower Lookup ─────────────────

    async def cell_tower_lookup(
        self, mcc: int, mnc: int, lac: int, cell_id: int
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

    # ── 3. Nominatim Forward Geocode (country/region) ───

    async def geocode_country_region(
        self, country_iso: str, location_name: Optional[str] = None
    ) -> Optional[GeoLocation]:
        """Get approximate coordinates for a country/region using Nominatim."""
        query = location_name or country_iso

        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "PhoneOSINT/1.0 (research project)"}
            async with session.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1},
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

    # ── 4. OpenCage Geocoding ──────────────────────────

    async def opencage_geocode(self, query: str) -> Optional[GeoLocation]:
        """Geocode using OpenCage API (free tier: 2500 req/day)."""
        if not settings.OPENCAGE_API_KEY:
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.opencagedata.com/geocode/v1/json",
                params={
                    "q": query,
                    "key": settings.OPENCAGE_API_KEY,
                    "limit": 1,
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("results"):
                        r = data["results"][0]
                        geo = r.get("geometry", {})
                        components = r.get("components", {})
                        result = GeoLocation()
                        result.latitude = geo.get("lat")
                        result.longitude = geo.get("lng")
                        result.address = r.get("formatted")
                        result.city = components.get("city") or components.get("town")
                        result.state = components.get("state")
                        result.country = components.get("country")
                        result.postal_code = components.get("postcode")
                        result.source = "opencage"
                        result.confidence = "estimated"
                        result.accuracy_km = 0.5
                        return result
        return None

    # ── 5. Phone Area Code Database ────────────────────

    AREA_CODE_DB: dict[str, dict[str, Any]] = {
        # US Area Codes (major cities)
        "212": {"city": "New York", "state": "NY", "country": "US", "lat": 40.7128, "lon": -74.0060},
        "213": {"city": "Los Angeles", "state": "CA", "country": "US", "lat": 34.0522, "lon": -118.2437},
        "312": {"city": "Chicago", "state": "IL", "country": "US", "lat": 41.8781, "lon": -87.6298},
        "415": {"city": "San Francisco", "state": "CA", "country": "US", "lat": 37.7749, "lon": -122.4194},
        "512": {"city": "Austin", "state": "TX", "country": "US", "lat": 30.2672, "lon": -97.7431},
        "646": {"city": "New York", "state": "NY", "country": "US", "lat": 40.7128, "lon": -74.0060},
        "713": {"city": "Houston", "state": "TX", "country": "US", "lat": 29.7604, "lon": -95.3698},
        "808": {"city": "Honolulu", "state": "HI", "country": "US", "lat": 21.3069, "lon": -157.8583},
        "917": {"city": "New York", "state": "NY", "country": "US", "lat": 40.7128, "lon": -74.0060},
        "305": {"city": "Miami", "state": "FL", "country": "US", "lat": 25.7617, "lon": -80.1918},
        "202": {"city": "Washington DC", "state": "DC", "country": "US", "lat": 38.9072, "lon": -77.0369},
        "617": {"city": "Boston", "state": "MA", "country": "US", "lat": 42.3601, "lon": -71.0589},
        "206": {"city": "Seattle", "state": "WA", "country": "US", "lat": 47.6062, "lon": -122.3321},
        "303": {"city": "Denver", "state": "CO", "country": "US", "lat": 39.7392, "lon": -104.9903},
        "404": {"city": "Atlanta", "state": "GA", "country": "US", "lat": 33.749, "lon": -84.388},
        "503": {"city": "Portland", "state": "OR", "country": "US", "lat": 45.5152, "lon": -122.6784},
        "702": {"city": "Las Vegas", "state": "NV", "country": "US", "lat": 36.1699, "lon": -115.1398},
        "858": {"city": "San Diego", "state": "CA", "country": "US", "lat": 32.7157, "lon": -117.1611},
        "972": {"city": "Dallas", "state": "TX", "country": "US", "lat": 32.7767, "lon": -96.7970},
        "201": {"city": "Jersey City", "state": "NJ", "country": "US", "lat": 40.7178, "lon": -74.0431},
        "602": {"city": "Phoenix", "state": "AZ", "country": "US", "lat": 33.4484, "lon": -112.0740},
        "818": {"city": "Burbank", "state": "CA", "country": "US", "lat": 34.1808, "lon": -118.3090},
        "909": {"city": "San Bernardino", "state": "CA", "country": "US", "lat": 34.1083, "lon": -117.2898},
        "551": {"city": "Jersey City", "state": "NJ", "country": "US", "lat": 40.7178, "lon": -74.0431},
        "347": {"city": "New York", "state": "NY", "country": "US", "lat": 40.7128, "lon": -74.0060},
        "929": {"city": "New York", "state": "NY", "country": "US", "lat": 40.7128, "lon": -74.0060},
        "628": {"city": "San Francisco", "state": "CA", "country": "US", "lat": 37.7749, "lon": -122.4194},
        "469": {"city": "Dallas", "state": "TX", "country": "US", "lat": 32.7767, "lon": -96.7970},
        "832": {"city": "Houston", "state": "TX", "country": "US", "lat": 29.7604, "lon": -95.3698},
        "214": {"city": "Dallas", "state": "TX", "country": "US", "lat": 32.7767, "lon": -96.7970},
        # UK Area Codes
        "20": {"city": "London", "state": "England", "country": "GB", "lat": 51.5074, "lon": -0.1278},
        "121": {"city": "Birmingham", "state": "England", "country": "GB", "lat": 52.4862, "lon": -1.8904},
        "131": {"city": "Edinburgh", "state": "Scotland", "country": "GB", "lat": 55.9533, "lon": -3.1883},
        "141": {"city": "Glasgow", "state": "Scotland", "country": "GB", "lat": 55.8642, "lon": -4.2518},
        "151": {"city": "Liverpool", "state": "England", "country": "GB", "lat": 53.4084, "lon": -2.9916},
        "161": {"city": "Manchester", "state": "England", "country": "GB", "lat": 53.4808, "lon": -2.2426},
        "113": {"city": "Leeds", "state": "England", "country": "GB", "lat": 53.8008, "lon": -1.5491},
        "114": {"city": "Sheffield", "state": "England", "country": "GB", "lat": 53.3811, "lon": -1.4701},
        "115": {"city": "Nottingham", "state": "England", "country": "GB", "lat": 52.9548, "lon": -1.1581},
        # India
        "11": {"city": "New Delhi", "state": "Delhi", "country": "IN", "lat": 28.6139, "lon": 77.2090},
        "22": {"city": "Mumbai", "state": "Maharashtra", "country": "IN", "lat": 19.0760, "lon": 72.8777},
        "80": {"city": "Bangalore", "state": "Karnataka", "country": "IN", "lat": 12.9716, "lon": 77.5946},
        "44": {"city": "Chennai", "state": "Tamil Nadu", "country": "IN", "lat": 13.0827, "lon": 80.2707},
        "33": {"city": "Chennai", "state": "Tamil Nadu", "country": "IN", "lat": 13.0827, "lon": 80.2707},
        "40": {"city": "Hyderabad", "state": "Telangana", "country": "IN", "lat": 17.3850, "lon": 78.4867},
        "48": {"city": "Kochi", "state": "Kerala", "country": "IN", "lat": 9.9312, "lon": 76.2673},
        "265": {"city": "Pune", "state": "Maharashtra", "country": "IN", "lat": 18.5204, "lon": 73.8567},
        "79": {"city": "Ahmedabad", "state": "Gujarat", "country": "IN", "lat": 23.0225, "lon": 72.5714},
        "32": {"city": "Kolkata", "state": "West Bengal", "country": "IN", "lat": 22.5726, "lon": 88.3639},
        "522": {"city": "Lucknow", "state": "Uttar Pradesh", "country": "IN", "lat": 26.8467, "lon": 80.9462},
    }

    async def area_code_lookup(self, national_number: str) -> Optional[GeoLocation]:
        """Estimate location from area code using built-in database."""
        # Try 3-digit area codes first (US/UK/etc)
        for length in [3, 2]:
            code = national_number[:length]
            if code in self.AREA_CODE_DB:
                entry = self.AREA_CODE_DB[code]
                result = GeoLocation()
                result.latitude = entry["lat"]
                result.longitude = entry["lon"]
                result.city = entry["city"]
                result.state = entry.get("state")
                result.country = entry["country"]
                result.source = "area-code-database"
                result.confidence = "estimated"
                result.accuracy_km = 25.0
                return result
        return None

    # ── 6. ip-api.com IP Geolocation ───────────────────

    async def ip_geolocation(self, ip_address: str) -> Optional[GeoLocation]:
        """Geolocate an IP address using ip-api.com."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://ip-api.com/json/{ip_address}",
                params={"fields": "status,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status") == "success":
                        result = GeoLocation()
                        result.latitude = data.get("lat")
                        result.longitude = data.get("lon")
                        result.city = data.get("city")
                        result.state = data.get("regionName")
                        result.country = data.get("countryCode")
                        result.postal_code = data.get("zip")
                        result.source = "ip-api"
                        result.confidence = "estimated"
                        result.accuracy_km = 10.0
                        return result
        return None

    # ── 7. Mozilla Location Service ────────────────────

    async def mozilla_location(
        self, cell_towers: list[dict[str, Any]], wifi_ap: Optional[list[dict[str, Any]]] = None
    ) -> Optional[GeoLocation]:
        """Geolocation via Mozilla Location Service (free, no API key)."""
        payload: dict[str, Any] = {}
        if cell_towers:
            payload["cellTowers"] = cell_towers
        if wifi_ap:
            payload["wifiAccessPoints"] = wifi_ap

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://location.services.mozilla.com/v1/search",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "location" in data:
                        result = GeoLocation()
                        result.latitude = data["location"].get("lat")
                        result.longitude = data["location"].get("lng")
                        result.source = "mozilla-location-service"
                        result.confidence = "public"
                        result.accuracy_km = data.get("accuracy", 1000) / 1000
                        return result
        return None

    # ── 8. Google Maps Geocoding (if key available) ────

    async def google_geocode(self, query: str) -> Optional[GeoLocation]:
        """Geocode using Google Maps API (requires GOOGLE_MAPS_API_KEY)."""
        api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
        if not api_key:
            return None

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": query, "key": api_key},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("results"):
                        r = data["results"][0]
                        loc = r.get("geometry", {}).get("location", {})
                        result = GeoLocation()
                        result.latitude = loc.get("lat")
                        result.longitude = loc.get("lng")
                        result.address = r.get("formatted_address")
                        result.source = "google-maps"
                        result.confidence = "verified"
                        result.accuracy_km = 0.1
                        return result
        return None

    # ── 9. Phone Number Carrier Region Mapping ─────────

    async def carrier_region_estimate(
        self, carrier: Optional[str], country_iso: Optional[str]
    ) -> Optional[GeoLocation]:
        """Estimate location based on carrier name and country."""
        if not carrier or not country_iso:
            return None

        # Use Nominatim with carrier + country for best estimate
        query = f"{carrier} headquarters {country_iso}"
        return await self.geocode_country_region(country_iso, query)

    # ── 10. Multi-Source Aggregation ───────────────────

    async def multi_source_geolocate(
        self,
        phone_number: str,
        country_iso: Optional[str] = None,
        location_name: Optional[str] = None,
        carrier: Optional[str] = None,
        ip_address: Optional[str] = None,
        mcc: Optional[int] = None,
        mnc: Optional[int] = None,
        lac: Optional[int] = None,
        cell_id: Optional[int] = None,
    ) -> GeoLocation:
        """
        Aggregate geolocation from 10+ sources and return best estimate.
        Sources are tried in parallel and the most specific result wins.
        """
        import asyncio

        sources: list[dict[str, Any]] = []
        candidates: list[GeoLocation] = []

        # Launch all source lookups in parallel
        tasks = []

        # 1. Area code database
        if phone_number:
            national = phone_number.lstrip("+")
            if country_iso and len(national) > len(country_iso):
                national = national[len(country_iso):]
            tasks.append(("area-code", self.area_code_lookup(national)))

        # 2. Nominatim geocode
        if location_name and country_iso:
            tasks.append(("nominatim", self.geocode_country_region(country_iso, location_name)))

        # 3. OpenCage
        if location_name and country_iso:
            tasks.append(("opencage", self.opencage_geocode(f"{location_name}, {country_iso}")))

        # 4. Cell tower lookup
        if mcc and mnc and lac is not None and cell_id is not None:
            if settings.OPENCELLID_API_KEY:
                tasks.append(("opencellid", self.cell_tower_lookup(mcc, mnc, lac, cell_id)))

        # 5. IP geolocation
        if ip_address:
            tasks.append(("ip-geo", self.ip_geolocation(ip_address)))

        # 6. Carrier region
        if carrier and country_iso:
            tasks.append(("carrier-region", self.carrier_region_estimate(carrier, country_iso)))

        # Execute all in parallel
        if not tasks:
            return GeoLocation()

        coros = [t[1] for t in tasks]
        results = await asyncio.gather(*coros, return_exceptions=True)

        # Collect valid results (filter exceptions and None results)
        for i, (name, _) in enumerate(tasks):
            if i < len(results) and not isinstance(results[i], Exception) and results[i] is not None:
                geo = results[i]
                if isinstance(geo, GeoLocation) and geo.latitude is not None:
                    candidates.append(geo)
                    sources.append({
                        "source": geo.source,
                        "latitude": geo.latitude,
                        "longitude": geo.longitude,
                        "accuracy_km": geo.accuracy_km,
                    })

        if not candidates:
            # Fallback: try Nominatim with just country
            if country_iso:
                fallback = await self.geocode_country_region(country_iso)
                if fallback:
                    candidates.append(fallback)
                    sources.append({
                        "source": fallback.source,
                        "latitude": fallback.latitude,
                        "longitude": fallback.longitude,
                        "accuracy_km": fallback.accuracy_km,
                    })

        if not candidates:
            result = GeoLocation()
            result.all_sources = sources
            return result

        # Pick best candidate (lowest accuracy_km wins)
        best = min(candidates, key=lambda g: g.accuracy_km or 99999)
        best.all_sources = sources
        return best


geolocation_service = GeolocationService()
