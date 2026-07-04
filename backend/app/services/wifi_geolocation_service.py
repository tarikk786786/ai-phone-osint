"""WiFi geolocation service — locate devices using WiFi access point BSSIDs and cell data."""

from __future__ import annotations

from typing import Any, Optional

import aiohttp


class WiFiGeoResult:
    """WiFi-based geolocation result."""

    def __init__(self) -> None:
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.accuracy_km: Optional[float] = None
        self.source: str = "unknown"
        self.confidence: str = "estimated"
        self.access_points: list[dict[str, Any]] = []
        self.cell_towers: list[dict[str, Any]] = []
        self.raw_data: dict[str, Any] = {}

    def to_dict(self) -> dict:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy_km": self.accuracy_km,
            "source": self.source,
            "confidence": self.confidence,
            "access_points": self.access_points,
            "cell_towers": self.cell_towers,
        }


class WiFiGeolocationService:
    """
    Geolocation using WiFi access points and cell towers.

    Uses Google Geolocation API-compatible format with free alternatives
    like Mozilla Location Service and custom cell tower databases.
    """

    # MCC/MNC to carrier mapping for common networks
    CARRIER_DB: dict[str, dict[str, str]] = {
        "310260": {"carrier": "T-Mobile US", "country": "US"},
        "311480": {"carrier": "Verizon", "country": "US"},
        "310410": {"carrier": "AT&T", "country": "US"},
        "302220": {"carrier": "Rogers", "country": "CA"},
        "26202": {"carrier": "Vodafone DE", "country": "DE"},
        "26201": {"carrier": "T-Mobile DE", "country": "DE"},
        "23415": {"carrier": "Vodafone UK", "country": "GB"},
        "23433": {"carrier": "EE UK", "country": "GB"},
        "46000": {"carrier": "China Mobile", "country": "CN"},
        "46001": {"carrier": "China Unicom", "country": "CN"},
        "46011": {"carrier": "China Telecom", "country": "CN"},
        "40410": {"carrier": "Airtel India", "country": "IN"},
        "40405": {"carrier": "BSNL India", "country": "IN"},
        "50501": {"carrier": "Telstra AU", "country": "AU"},
        "25001": {"carrier": "MTS RU", "country": "RU"},
        "25099": {"carrier": "Beeline RU", "country": "RU"},
        "44010": {"carrier": "NTT Docomo JP", "country": "JP"},
        "44020": {"carrier": "Softbank JP", "country": "JP"},
        "45005": {"carrier": "SK Telecom KR", "country": "KR"},
        "45002": {"carrier": "KT KR", "country": "KR"},
        "63902": {"carrier": "Safaricom KE", "country": "KE"},
        "62130": {"carrier": "Airtel NG", "country": "NG"},
    }

    async def locate_by_cell_tower(
        self,
        mcc: int,
        mnc: int,
        lac: int,
        cell_id: int,
        signal_strength: Optional[int] = None,
    ) -> Optional[WiFiGeoResult]:
        """Locate using cell tower information via OpenCellID."""
        result = WiFiGeoResult()
        result.cell_towers.append({
            "mcc": mcc,
            "mnc": mnc,
            "lac": lac,
            "cell_id": cell_id,
            "signal_strength": signal_strength,
        })

        # Try Mozilla Location Service (free, no key)
        mozilla_result = await self._mozilla_location_service(
            mcc, mnc, lac, cell_id
        )
        if mozilla_result:
            result.latitude = mozilla_result.get("lat")
            result.longitude = mozilla_result.get("lon")
            result.accuracy_km = mozilla_result.get("accuracy", 1000) / 1000
            result.source = "mozilla-location-service"
            result.confidence = "public"
            result.raw_data = mozilla_result
            return result

        return None

    async def locate_by_wifi_bssids(
        self,
        bssids: list[dict[str, Any]],
    ) -> Optional[WiFiGeoResult]:
        """
        Locate using WiFi access point BSSIDs.

        Each entry should have: mac (BSSID), signal (RSSI in dBm).
        Uses Mozilla Location Service WiFi API.
        """
        result = WiFiGeoResult()
        result.access_points = bssids

        # Build request for Mozilla Location Service
        wifi_data = []
        for ap in bssids:
            wifi_entry = {
                "key": ap.get("mac", ap.get("bssid", "")),
                "frequency": ap.get("frequency", 2412),
                "signal": ap.get("signal", -50),
            }
            wifi_data.append(wifi_entry)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://location.services.mozilla.com/v1/search",
                    json={"wifiAccessPoints": wifi_data},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "location" in data:
                            result.latitude = data["location"].get("lat")
                            result.longitude = data["location"].get("lng")
                            result.accuracy_km = data.get("accuracy", 1000) / 1000
                            result.source = "mozilla-wifi"
                            result.confidence = "public"
                            result.raw_data = data
                            return result
        except Exception:
            pass

        return None

    async def locate_combined(
        self,
        cell_towers: Optional[list[dict[str, Any]]] = None,
        wifi_access_points: Optional[list[dict[str, Any]]] = None,
    ) -> Optional[WiFiGeoResult]:
        """
        Combined cell tower + WiFi geolocation for best accuracy.
        Uses Mozilla Location Service which accepts both.
        """
        result = WiFiGeoResult()

        cell_data = []
        wifi_data = []

        if cell_towers:
            for ct in cell_towers:
                cell_data.append({
                    "radio": ct.get("radio", "gsm"),
                    "mcc": ct.get("mcc"),
                    "mnc": ct.get("mnc"),
                    "lac": ct.get("lac"),
                    "cid": ct.get("cell_id", ct.get("cid")),
                    "signal": ct.get("signal", -80),
                })
            result.cell_towers = cell_towers

        if wifi_access_points:
            for ap in wifi_access_points:
                wifi_data.append({
                    "key": ap.get("mac", ap.get("bssid", "")),
                    "frequency": ap.get("frequency", 2412),
                    "signal": ap.get("signal", -50),
                })
            result.access_points = wifi_access_points

        if not cell_data and not wifi_data:
            return None

        try:
            payload = {}
            if cell_data:
                payload["cellTowers"] = cell_data
            if wifi_data:
                payload["wifiAccessPoints"] = wifi_data

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://location.services.mozilla.com/v1/search",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "location" in data:
                            result.latitude = data["location"].get("lat")
                            result.longitude = data["location"].get("lng")
                            result.accuracy_km = data.get("accuracy", 1000) / 1000
                            result.source = "mozilla-combined"
                            result.confidence = "public"
                            result.raw_data = data
                            return result
        except Exception:
            pass

        return None

    async def _mozilla_location_service(
        self, mcc: int, mnc: int, lac: int, cell_id: int
    ) -> Optional[dict]:
        """Query Mozilla Location Service for cell tower geolocation."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://location.services.mozilla.com/v1/search",
                    json={
                        "cellTowers": [
                            {
                                "radio": "gsm",
                                "mcc": mcc,
                                "mnc": mnc,
                                "lac": lac,
                                "cid": cell_id,
                            }
                        ]
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "location" in data:
                            return {
                                "lat": data["location"].get("lat"),
                                "lon": data["location"].get("lng"),
                                "accuracy": data.get("accuracy", 1000),
                            }
        except Exception:
            pass
        return None

    def get_carrier_info(self, mcc: int, mnc: int) -> Optional[dict[str, str]]:
        """Look up carrier information from MCC/MNC code."""
        # Try both zero-padded and raw formats
        key_padded = f"{mcc:03d}{mnc:03d}"
        key_raw = f"{mcc}{mnc}"
        return self.CARRIER_DB.get(key_padded) or self.CARRIER_DB.get(key_raw)


wifi_geolocation_service = WiFiGeolocationService()
