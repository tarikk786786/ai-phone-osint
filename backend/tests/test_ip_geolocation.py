"""Tests for IP geolocation service."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ip_geolocation_service import IPGeolocationService, IPGeoResult, ip_geolocation_service


class TestIPGeoResult:
    """Test suite for IPGeoResult data class."""

    def test_default_values(self):
        """Default values should be properly initialized."""
        result = IPGeoResult()
        assert result.ip == ""
        assert result.country is None
        assert result.latitude is None
        assert result.longitude is None
        assert result.source == "unknown"
        assert result.accuracy_km is None

    def test_to_dict_serialization(self):
        """to_dict should return a proper dictionary."""
        result = IPGeoResult()
        result.ip = "8.8.8.8"
        result.country = "United States"
        result.latitude = 37.7749
        result.longitude = -122.4194
        result.source = "ip-api.com"

        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["ip"] == "8.8.8.8"
        assert d["country"] == "United States"
        assert d["latitude"] == 37.7749
        assert d["longitude"] == -122.4194
        assert d["source"] == "ip-api.com"

    def test_to_dict_has_all_fields(self):
        """to_dict should include all expected fields."""
        result = IPGeoResult()
        d = result.to_dict()
        expected_keys = [
            "ip", "country", "country_code", "region", "city",
            "latitude", "longitude", "postal_code", "timezone",
            "isp", "org", "as_number", "hosting", "proxy", "vpn",
            "source", "accuracy_km",
        ]
        for key in expected_keys:
            assert key in d, f"Missing key: {key}"


class TestIPGeolocationService:
    """Test suite for IPGeolocationService."""

    def setup_method(self):
        self.service = IPGeolocationService()

    @pytest.mark.asyncio
    async def test_lookup_returns_first_success(self):
        """lookup should return the first successful result from parallel APIs."""
        mock_result = IPGeoResult()
        mock_result.ip = "8.8.8.8"
        mock_result.latitude = 37.7749
        mock_result.longitude = -122.4194
        mock_result.source = "ip-api.com"

        with patch.object(self.service, '_lookup_ipapi', return_value=mock_result):
            result = await self.service.lookup("8.8.8.8")
            assert result is not None
            assert result.ip == "8.8.8.8"
            assert result.latitude == 37.7749

    @pytest.mark.asyncio
    async def test_lookup_returns_none_when_all_fail(self):
        """lookup should return None when all APIs fail."""
        with patch.object(self.service, '_lookup_ipapi', return_value=None):
            with patch.object(self.service, '_lookup_ipwhois', return_value=None):
                with patch.object(self.service, '_lookup_ipinfo', return_value=None):
                    result = await self.service.lookup("8.8.8.8")
                    assert result is None

    @pytest.mark.asyncio
    async def test_lookup_falls_back_to_second_api(self):
        """lookup should try second API when first returns None."""
        mock_result = IPGeoResult()
        mock_result.ip = "8.8.8.8"
        mock_result.latitude = 37.7749
        mock_result.source = "ipwho.is"

        with patch.object(self.service, '_lookup_ipapi', return_value=None):
            with patch.object(self.service, '_lookup_ipwhois', return_value=mock_result):
                result = await self.service.lookup("8.8.8.8")
                assert result is not None
                assert result.source == "ipwho.is"

    @pytest.mark.asyncio
    async def test_lookup_handles_exceptions(self):
        """lookup should handle exceptions gracefully."""
        async def mock_exception(*args, **kwargs):
            raise Exception("API error")

        with patch.object(self.service, '_lookup_ipapi', side_effect=mock_exception):
            with patch.object(self.service, '_lookup_ipwhois', side_effect=mock_exception):
                with patch.object(self.service, '_lookup_ipinfo', side_effect=mock_exception):
                    result = await self.service.lookup("8.8.8.8")
                    assert result is None

    @pytest.mark.asyncio
    async def test_resolve_domain_success(self):
        """resolve_domain should resolve domain to IP and geolocate."""
        mock_result = IPGeoResult()
        mock_result.ip = "142.250.80.46"
        mock_result.latitude = 37.7749

        with patch('app.services.ip_geolocation_service.socket.gethostbyname', return_value="142.250.80.46"):
            with patch.object(self.service, 'lookup', return_value=mock_result):
                result = await self.service.resolve_domain("google.com")
                assert result is not None
                assert result.ip == "142.250.80.46"

    @pytest.mark.asyncio
    async def test_resolve_domain_failure(self):
        """resolve_domain should return None for unresolvable domains."""
        import socket
        with patch('app.services.ip_geolocation_service.socket.gethostbyname', side_effect=socket.gaierror("DNS error")):
            result = await self.service.resolve_domain("nonexistent.invalid")
            assert result is None


class TestIPGeolocationServiceSingleton:
    """Test that the service is properly exported as singleton."""

    def test_singleton_exists(self):
        """ip_geolocation_service should be a singleton instance."""
        assert ip_geolocation_service is not None
        assert isinstance(ip_geolocation_service, IPGeolocationService)
