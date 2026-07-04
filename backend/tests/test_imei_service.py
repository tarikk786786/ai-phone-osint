"""Tests for IMEI lookup service."""

from __future__ import annotations

import pytest
from app.services.imei_service import IMEILookupService, IMEIResult, imei_lookup_service


class TestIMEIValidation:
    """Test suite for IMEI validation (Luhn algorithm)."""

    def setup_method(self):
        self.service = IMEILookupService()

    def test_valid_imei_15_digits(self):
        """A valid 15-digit IMEI should pass Luhn check."""
        assert self.service.validate_imei("353456789012348") is True

    def test_valid_imei_with_dashes(self):
        """IMEI with dashes should be validated correctly."""
        assert self.service.validate_imei("353-456-789-012-348") is True

    def test_valid_imei_with_spaces(self):
        """IMEI with spaces should be validated correctly."""
        assert self.service.validate_imei("353 456 789 012 348") is True

    def test_invalid_imei_wrong_checksum(self):
        """IMEI with wrong checksum digit should fail."""
        assert self.service.validate_imei("353456789012346") is False

    def test_invalid_imei_too_short(self):
        """IMEI shorter than 15 digits should fail."""
        assert self.service.validate_imei("35345678901234") is False

    def test_invalid_imei_too_long(self):
        """IMEI longer than 15 digits should fail."""
        assert self.service.validate_imei("3534567890123456") is False

    def test_invalid_imei_letters(self):
        """IMEI containing letters should fail."""
        assert self.service.validate_imei("35345678901234A") is False

    def test_invalid_imei_empty(self):
        """Empty string should fail."""
        assert self.service.validate_imei("") is False

    def test_valid_imei_all_zeros(self):
        """All zeros IMEI passes Luhn (sum=0)."""
        assert self.service.validate_imei("000000000000000") is True

    def test_valid_imei_check_digit(self):
        """IMEI with correct check digit should pass Luhn."""
        assert self.service.validate_imei("999999999999994") is True

    def test_invalid_imei_non_numeric(self):
        """Non-numeric IMEI should fail."""
        assert self.service.validate_imei("ABCDEFGHIJKLMNO") is False


class TestIMEITACExtraction:
    """Test suite for TAC (Type Allocation Code) extraction."""

    def setup_method(self):
        self.service = IMEILookupService()

    def test_extract_tac_normal(self):
        """Should extract first 8 digits as TAC."""
        tac = self.service.extract_tac("353456789012348")
        assert tac == "35345678"

    def test_extract_tac_with_dashes(self):
        """Should handle IMEI with dashes."""
        tac = self.service.extract_tac("353-456-789-012-348")
        assert tac == "35345678"

    def test_extract_tac_with_spaces(self):
        """Should handle IMEI with spaces."""
        tac = self.service.extract_tac("353 456 789 012 348")
        assert tac == "35345678"


class TestIMEIResult:
    """Test suite for IMEIResult data class."""

    def test_default_values(self):
        """Default values should be properly initialized."""
        result = IMEIResult()
        assert result.imei == ""
        assert result.is_valid is False
        assert result.brand is None
        assert result.source == "local"

    def test_to_dict_serialization(self):
        """to_dict should return a proper dictionary with all fields."""
        result = IMEIResult()
        result.imei = "353456789012348"
        result.is_valid = True
        result.tac = "35345678"
        result.brand = "Samsung"
        result.model = "Galaxy S8"

        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["imei"] == "353456789012348"
        assert d["is_valid"] is True
        assert d["tac"] == "35345678"
        assert d["brand"] == "Samsung"
        assert d["model"] == "Galaxy S8"

    def test_to_dict_has_all_fields(self):
        """to_dict should include all expected fields."""
        result = IMEIResult()
        d = result.to_dict()
        expected_keys = [
            "imei", "is_valid", "device_name", "manufacturer", "brand",
            "model", "device_type", "os", "sim_count", "release_date",
            "country", "is_stolen", "blacklisted", "tac", "source", "raw_data",
        ]
        for key in expected_keys:
            assert key in d, f"Missing key: {key}"

    def test_merge_device_data(self):
        """Test merging device data from API response."""
        result = IMEIResult()
        result.imei = "353456789012348"
        result.is_valid = True
        result.tac = "35345678"

        service = IMEILookupService()
        service._merge_device_data(result, {
            "device_name": "Samsung Galaxy S8",
            "brand": "Samsung",
            "manufacturer": "Samsung Electronics",
            "model": "SM-G950F",
            "type": "Smartphone",
            "os": "Android",
        })

        assert result.device_name == "Samsung Galaxy S8"
        assert result.brand == "Samsung"
        assert result.manufacturer == "Samsung Electronics"
        assert result.model == "SM-G950F"
        assert result.device_type == "Smartphone"
        assert result.os == "Android"
        assert result.source == "api"


class TestIMEILookup:
    """Test suite for IMEI device lookup."""

    def setup_method(self):
        self.service = IMEILookupService()

    @pytest.mark.asyncio
    async def test_lookup_invalid_imei_returns_invalid(self):
        """Invalid IMEI should return is_valid=False."""
        result = await self.service.lookup("12345")
        assert result.is_valid is False
        assert result.imei == "12345"
        assert result.source == "local"

    @pytest.mark.asyncio
    async def test_lookup_valid_imei_format(self):
        """Valid IMEI should have is_valid=True and TAC populated."""
        result = await self.service.lookup("353456789012348")
        assert result.is_valid is True
        assert result.tac == "35345678"
        assert result.imei == "353456789012348"

    @pytest.mark.asyncio
    async def test_lookup_strips_dashes(self):
        """IMEI with dashes should be normalized."""
        result = await self.service.lookup("353-456-789-012-348")
        assert result.imei == "353456789012348"
        assert result.is_valid is True

    @pytest.mark.asyncio
    async def test_lookup_result_has_all_fields(self):
        """Result should have all expected fields."""
        result = await self.service.lookup("353456789012348")
        result_dict = result.to_dict()
        assert "imei" in result_dict
        assert "is_valid" in result_dict
        assert "tac" in result_dict
        assert "brand" in result_dict
        assert "source" in result_dict


class TestIMEIServiceSingleton:
    """Test that the service is properly exported as singleton."""

    def test_singleton_exists(self):
        """imei_lookup_service should be a singleton instance."""
        assert imei_lookup_service is not None
        assert isinstance(imei_lookup_service, IMEILookupService)
