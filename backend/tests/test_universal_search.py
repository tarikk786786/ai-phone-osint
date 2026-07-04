"""Tests for Universal Search input detection and location tools."""

from __future__ import annotations

import pytest
from app.api.routes.location_tools import detect_input_type


class TestInputTypeDetection:
    """Test suite for the detect_input_type function."""

    # ── Phone Number Detection ─────────────────────────

    def test_phone_us_with_plus(self):
        """US phone number with + prefix should detect as phone."""
        input_type, value = detect_input_type("+14155552671")
        assert input_type == "phone"
        assert value == "+14155552671"

    def test_phone_uk_with_plus(self):
        """UK phone number with + prefix should detect as phone."""
        input_type, value = detect_input_type("+442079460818")
        assert input_type == "phone"
        assert value == "+442079460818"

    def test_phone_india_with_plus(self):
        """Indian phone number with + prefix should detect as phone."""
        input_type, value = detect_input_type("+919876543210")
        assert input_type == "phone"

    def test_phone_without_plus(self):
        """Phone number without + prefix should detect as phone."""
        input_type, value = detect_input_type("4155552671")
        assert input_type == "phone"

    def test_phone_with_country_code_00(self):
        """Phone number with 00 prefix should detect as phone."""
        input_type, value = detect_input_type("0014155552671")
        assert input_type == "phone"

    def test_phone_short_number(self):
        """Short number (7+ digits) should detect as phone."""
        input_type, value = detect_input_type("5551234")
        assert input_type == "phone"

    def test_phone_with_dashes(self):
        """Phone number with dashes should detect as phone."""
        input_type, value = detect_input_type("+1-415-555-2671")
        assert input_type == "phone"

    # ── IMEI Detection ─────────────────────────────────

    def test_valid_imei_15_digits(self):
        """Valid 15-digit IMEI (passes Luhn) should detect as imei."""
        input_type, value = detect_input_type("353456789012348")
        assert input_type == "imei"
        assert value == "353456789012348"

    def test_valid_imei_with_dashes(self):
        """Valid IMEI with dashes should detect as imei."""
        input_type, value = detect_input_type("353-456-789-012-348")
        assert input_type == "imei"
        assert value == "353456789012348"

    def test_invalid_imei_falls_back_to_phone(self):
        """Invalid IMEI (fails Luhn) starting with country code falls back to phone."""
        input_type, value = detect_input_type("123456789012345")
        # Starts with 1 (US country code) → detected as phone before Luhn check
        assert input_type == "phone"

    def test_imei_all_nines(self):
        """IMEI of all 9s with valid check digit passes Luhn."""
        input_type, value = detect_input_type("999999999999994")
        assert input_type == "imei"

    # ── IP Address Detection ───────────────────────────

    def test_ipv4_address(self):
        """Standard IPv4 address should detect as ip."""
        input_type, value = detect_input_type("8.8.8.8")
        assert input_type == "ip"
        assert value == "8.8.8.8"

    def test_ipv4_address_private(self):
        """Private IPv4 address should detect as ip."""
        input_type, value = detect_input_type("192.168.1.1")
        assert input_type == "ip"
        assert value == "192.168.1.1"

    def test_ipv4_address_broadcast(self):
        """Broadcast address should detect as ip."""
        input_type, value = detect_input_type("255.255.255.255")
        assert input_type == "ip"

    def test_ipv4_invalid_octet(self):
        """IPv4 with octet > 255 should NOT detect as ip."""
        input_type, value = detect_input_type("999.1.1.1")
        assert input_type != "ip"

    def test_ipv6_address(self):
        """IPv6 address should detect as ip."""
        input_type, value = detect_input_type("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        assert input_type == "ip"

    def test_ipv6_short(self):
        """Short IPv6 address should detect as ip."""
        input_type, value = detect_input_type("::1")
        assert input_type == "ip"

    # ── WiFi BSSID Detection ───────────────────────────

    def test_wifi_bssid_colon_separated(self):
        """MAC address with colons should detect as wifi_bssid."""
        input_type, value = detect_input_type("AA:BB:CC:DD:EE:FF")
        assert input_type == "wifi_bssid"
        assert value == "AA:BB:CC:DD:EE:FF"

    def test_wifi_bssid_dash_separated(self):
        """MAC address with dashes should detect as wifi_bssid."""
        input_type, value = detect_input_type("AA-BB-CC-DD-EE-FF")
        assert input_type == "wifi_bssid"
        assert value == "AA-BB-CC-DD-EE-FF"

    def test_wifi_bssid_lowercase(self):
        """Lowercase MAC address should be normalized to uppercase."""
        input_type, value = detect_input_type("aa:bb:cc:dd:ee:ff")
        assert input_type == "wifi_bssid"
        assert value == "AA:BB:CC:DD:EE:FF"

    def test_wifi_bssid_mixed_case(self):
        """Mixed case MAC address should be normalized to uppercase."""
        input_type, value = detect_input_type("aA:Bb:Cc:Dd:Ee:Ff")
        assert input_type == "wifi_bssid"
        assert value == "AA:BB:CC:DD:EE:FF"

    # ── Domain Detection ───────────────────────────────

    def test_domain_simple(self):
        """Simple domain should detect as domain."""
        input_type, value = detect_input_type("example.com")
        assert input_type == "domain"
        assert value == "example.com"

    def test_domain_with_subdomain(self):
        """Domain with subdomain should detect as domain."""
        input_type, value = detect_input_type("www.example.com")
        assert input_type == "domain"
        assert value == "www.example.com"

    def test_domain_with_many_subdomains(self):
        """Domain with multiple subdomains should detect as domain."""
        input_type, value = detect_input_type("a.b.c.example.com")
        assert input_type == "domain"

    def test_domain_with_hyphen(self):
        """Domain with hyphen should detect as domain."""
        input_type, value = detect_input_type("my-site.example.com")
        assert input_type == "domain"

    def test_domain_with_numbers(self):
        """Domain with numbers should detect as domain."""
        input_type, value = detect_input_type("test123.example.com")
        assert input_type == "domain"

    # ── Coordinates Detection ──────────────────────────

    def test_coordinates_lat_lon(self):
        """Comma-separated coordinates should detect as coordinates."""
        input_type, value = detect_input_type("40.7128,-74.0060")
        assert input_type == "coordinates"
        assert value == "40.7128,-74.0060"

    def test_coordinates_negative(self):
        """Coordinates with negative values should detect as coordinates."""
        input_type, value = detect_input_type("-33.8688,151.2093")
        assert input_type == "coordinates"

    def test_coordinates_with_spaces(self):
        """Coordinates with spaces around comma should detect."""
        input_type, value = detect_input_type("40.7128, -74.0060")
        assert input_type == "coordinates"

    def test_coordinates_integer(self):
        """Integer coordinates should detect as coordinates."""
        input_type, value = detect_input_type("40,-74")
        assert input_type == "coordinates"

    def test_coordinates_out_of_range(self):
        """Coordinates out of range should NOT detect as coordinates."""
        input_type, value = detect_input_type("999,999")
        assert input_type != "coordinates"

    # ── Unknown Input ──────────────────────────────────

    def test_unknown_input_empty(self):
        """Empty string should detect as unknown."""
        input_type, value = detect_input_type("")
        assert input_type == "unknown"

    def test_unknown_input_short_text(self):
        """Short random text should detect as unknown."""
        input_type, value = detect_input_type("hello")
        assert input_type == "unknown"

    def test_unknown_input_special_chars(self):
        """Special characters should detect as unknown."""
        input_type, value = detect_input_type("!@#$%^&*()")
        assert input_type == "unknown"

    # ── Edge Cases ─────────────────────────────────────

    def test_whitespace_trimmed(self):
        """Leading/trailing whitespace should be trimmed."""
        input_type, value = detect_input_type("  8.8.8.8  ")
        assert input_type == "ip"
        assert value == "8.8.8.8"

    def test_mixed_case_domain(self):
        """Mixed case domain should be normalized to lowercase."""
        input_type, value = detect_input_type("EXAMPLE.COM")
        assert input_type == "domain"
        assert value == "example.com"


class TestDetectInputTypeCoverage:
    """Test that all expected input types can be detected."""

    def test_all_types_can_be_detected(self):
        """Verify that each input type has at least one working test case."""
        test_cases = {
            "phone": "+14155552671",
            "imei": "353456789012348",
            "ip": "8.8.8.8",
            "wifi_bssid": "AA:BB:CC:DD:EE:FF",
            "domain": "example.com",
            "coordinates": "40.7128,-74.0060",
        }
        for expected_type, test_input in test_cases.items():
            detected_type, _ = detect_input_type(test_input)
            assert detected_type == expected_type, f"Failed for {expected_type}: got {detected_type}"
