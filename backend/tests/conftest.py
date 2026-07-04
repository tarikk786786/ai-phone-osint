"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_phone_numbers() -> dict[str, str]:
    """Sample phone numbers for testing across various countries."""
    return {
        "us": "+14155552671",
        "uk": "+442079460818",
        "india": "+919876543210",
        "germany": "+49301234567",
        "france": "+33123456789",
        "australia": "+61212345678",
        "japan": "+81312345678",
        "brazil": "+551112345678",
        "china": "+861012345678",
        "russia": "+74951234567",
        "uae": "+971501234567",
        "nigeria": "+2348012345678",
    }


@pytest.fixture
def mock_phone_data() -> dict:
    """Mock phone validation data for testing."""
    return {
        "is_valid": True,
        "is_possible": True,
        "country_code": 1,
        "country_iso": "US",
        "country_name": "United States",
        "location": "California",
        "carrier": "AT&T",
        "line_type": "mobile",
        "timezones": ["America/Los_Angeles"],
        "formatted_international": "+1 415-555-2671",
        "formatted_national": "(415) 555-2671",
        "e164": "+14155552671",
    }
