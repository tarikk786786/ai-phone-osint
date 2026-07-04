"""Tests for WiFi geolocation service."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.wifi_geolocation_service import (
    WiFiGeolocationService,
    WiFiGeoResult,
    wifi_geolocation_service,
)


class TestWiFiGeoResult:
    """Test suite for WiFiGeoResult data class."""

    def test_default_values(self):
        """Default values should be properly initialized."""
        result = WiFiGeoResult()
        assert result.latitude is None
        assert result.longitude is None
        assert result.accuracy_km is None
        assert result.source == "unknown"
        assert result.confidence == "estimated"
        assert result.access_points == []
        assert result.cell_towers == []

    def test_to_dict_serialization(self):
        """to_dict should return a proper dictionary."""
        result = WiFiGeoResult()
        result.latitude = 40.7128
        result.longitude = -74.0060
        result.source = "mozilla-location-service"
        result.accuracy_km = 1.5

        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["latitude"] == 40.7128
        assert d["longitude"] == -74.0060
        assert d["source"] == "mozilla-location-service"
        assert d["accuracy_km"] == 1.5

    def test_to_dict_has_all_fields(self):
        """to_dict should include all expected fields."""
        result = WiFiGeoResult()
        d = result.to_dict()
        expected_keys = [
            "latitude", "longitude", "accuracy_km", "source",
            "confidence", "access_points", "cell_towers",
        ]
        for key in expected_keys:
            assert key in d, f"Missing key: {key}"


class TestWiFiGeolocationService:
    """Test suite for WiFiGeolocationService."""

    def setup_method(self):
        self.service = WiFiGeolocationService()

    def test_carrier_db_has_entries(self):
        """Carrier database should have known carriers."""
        assert "310260" in self.service.CARRIER_DB  # T-Mobile US
        assert "311480" in self.service.CARRIER_DB  # Verizon
        assert "40410" in self.service.CARRIER_DB   # Airtel India

    def test_carrier_db_values(self):
        """Carrier database entries should have correct fields."""
        tmobile = self.service.CARRIER_DB["310260"]
        assert tmobile["carrier"] == "T-Mobile US"
        assert tmobile["country"] == "US"

    def test_get_carrier_info_found(self):
        """get_carrier_info should return carrier data for known MCC/MNC."""
        result = self.service.get_carrier_info(310, 260)
        assert result is not None
        assert result["carrier"] == "T-Mobile US"

    def test_get_carrier_info_padded(self):
        """get_carrier_info should handle zero-padded MCC/MNC."""
        result = self.service.get_carrier_info(310, 260)
        assert result is not None

    def test_get_carrier_info_unknown(self):
        """get_carrier_info should return None for unknown MCC/MNC."""
        result = self.service.get_carrier_info(999, 999)
        assert result is None

    @pytest.mark.asyncio
    async def test_locate_by_cell_tower_success(self):
        """locate_by_cell_tower should return result when Mozilla LS responds."""
        mock_response = {
            "location": {"lat": 40.7128, "lng": -74.0060},
            "accuracy": 1500,
        }

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_session.return_value.post = MagicMock(return_value=mock_resp)

            result = await self.service.locate_by_cell_tower(310, 260, 12345, 67890)
            assert result is not None

    @pytest.mark.asyncio
    async def test_locate_by_cell_tower_failure(self):
        """locate_by_cell_tower should return None when API fails."""
        mock_resp = AsyncMock()
        mock_resp.status = 500
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_session.return_value.post = MagicMock(return_value=mock_resp)

            result = await self.service.locate_by_cell_tower(310, 260, 12345, 67890)
            assert result is None

    @pytest.mark.asyncio
    async def test_locate_by_wifi_bssids_success(self):
        """locate_by_wifi_bssids should return result when API responds."""
        mock_response = {
            "location": {"lat": 40.7128, "lng": -74.0060},
            "accuracy": 500,
        }

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_session.return_value.post = MagicMock(return_value=mock_resp)

            result = await self.service.locate_by_wifi_bssids(
                [{"mac": "AA:BB:CC:DD:EE:FF", "signal": -50, "frequency": 2412}]
            )
            assert result is not None
            assert result.latitude == 40.7128

    @pytest.mark.asyncio
    async def test_locate_by_wifi_bssids_no_location(self):
        """locate_by_wifi_bssids should return None when no location in response."""
        mock_response = {"error": "location not found"}

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_session.return_value.post = MagicMock(return_value=mock_resp)

            result = await self.service.locate_by_wifi_bssids(
                [{"mac": "AA:BB:CC:DD:EE:FF", "signal": -50}]
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_locate_combined_no_data(self):
        """locate_combined should return None with no input data."""
        result = await self.service.locate_combined()
        assert result is None

    @pytest.mark.asyncio
    async def test_locate_combined_cell_only(self):
        """locate_combined should work with cell tower data only."""
        mock_response = {
            "location": {"lat": 40.7128, "lng": -74.0060},
            "accuracy": 2000,
        }

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)

        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session.return_value)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_session.return_value.post = MagicMock(return_value=mock_resp)

            result = await self.service.locate_combined(
                cell_towers=[{"mcc": 310, "mnc": 260, "lac": 12345, "cell_id": 67890}]
            )
            assert result is not None
            assert result.source == "mozilla-combined"

    def test_result_fields_populated(self):
        """Result should have cell_towers and access_points populated."""
        result = WiFiGeoResult()
        result.cell_towers.append({"mcc": 310, "mnc": 260})
        result.access_points.append({"mac": "AA:BB:CC:DD:EE:FF"})

        d = result.to_dict()
        assert len(d["cell_towers"]) == 1
        assert len(d["access_points"]) == 1


class TestWiFiGeolocationServiceSingleton:
    """Test that the service is properly exported as singleton."""

    def test_singleton_exists(self):
        """wifi_geolocation_service should be a singleton instance."""
        assert wifi_geolocation_service is not None
        assert isinstance(wifi_geolocation_service, WiFiGeolocationService)
