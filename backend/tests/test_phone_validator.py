"""Tests for PhoneValidator service."""

from __future__ import annotations

import pytest
from app.services.phone_validator import PhoneValidator, phone_validator


class TestPhoneValidator:
    """Test suite for PhoneValidator."""

    def test_valid_us_number(self):
        """Validate a standard US phone number."""
        result = phone_validator.validate("+14155552671")
        assert result.is_valid is True
        assert result.is_possible is True
        assert result.country_code == 1
        assert result.country_iso == "US"
        assert result.e164 == "+14155552671"
        assert "America/" in result.timezones[0] if result.timezones else True

    def test_valid_international_number(self):
        """Validate a UK phone number."""
        result = phone_validator.validate("+442079460818")
        assert result.is_valid is True
        assert result.country_code == 44
        assert result.country_iso == "GB"

    def test_invalid_number(self):
        """An obviously invalid number should fail validation."""
        result = phone_validator.validate("123")
        assert result.is_valid is False

    def test_indian_number(self):
        """Validate an Indian phone number."""
        result = phone_validator.validate("+919876543210")
        assert result.is_valid is True
        assert result.country_code == 91
        assert result.country_iso == "IN"

    def test_number_with_country_hint(self):
        """Test parsing with a default country hint."""
        result = phone_validator.validate("(555) 123-4567", "US")
        assert result.is_valid is True
        assert result.country_code == 1

    def test_line_type_detection(self):
        """Test that line type is detected for known mobile numbers."""
        result = phone_validator.validate("+14155552671")
        assert result.line_type in ("mobile", "fixed_line", "fixed_line_or_mobile")

    def test_formatting(self):
        """Test phone number formatting."""
        result = phone_validator.validate("+14155552671")
        assert result.formatted_international == "+1 415-555-2671"
        assert result.formatted_national == "(415) 555-2671"
