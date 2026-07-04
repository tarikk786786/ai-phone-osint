"""Phone validation and parsing service — wraps libphonenumbers."""

from __future__ import annotations

from typing import Optional

import phonenumbers
from phonenumbers import carrier as ph_carrier
from phonenumbers import geocoder as ph_geocoder
from phonenumbers import timezone as ph_timezone


class PhoneValidationResult:
    """Structured result from phone number validation."""

    def __init__(self) -> None:
        self.is_valid: bool = False
        self.is_possible: bool = False
        self.country_code: Optional[int] = None
        self.country_iso: Optional[str] = None
        self.country_name: Optional[str] = None
        self.location: Optional[str] = None
        self.carrier: Optional[str] = None
        self.line_type: Optional[str] = None
        self.timezones: list[str] = []
        self.formatted_international: Optional[str] = None
        self.formatted_national: Optional[str] = None
        self.e164: Optional[str] = None
        self.national_number: Optional[int] = None
        self.extension: Optional[str] = None
        self.is_mobile: bool = False
        self.is_fixed_line: bool = False
        self.is_voip: bool = False
        self.is_toll_free: bool = False
        self.is_premium_rate: bool = False
        self.is_shared_cost: bool = False
        self.is_personal_number: bool = False
        self.is_uan: bool = False  # Universal Access Number
        self.is_voicemail: bool = False
        self.is_pager: bool = False
        self.is_unknown: bool = True

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "is_possible": self.is_possible,
            "country_code": self.country_code,
            "country_iso": self.country_iso,
            "country_name": self.country_name,
            "location": self.location,
            "carrier": self.carrier,
            "line_type": self.line_type,
            "timezones": self.timezones,
            "formatted_international": self.formatted_international,
            "formatted_national": self.formatted_national,
            "e164": self.e164,
            "national_number": self.national_number,
            "extension": self.extension,
            "is_mobile": self.is_mobile,
            "is_fixed_line": self.is_fixed_line,
            "is_voip": self.is_voip,
            "is_toll_free": self.is_toll_free,
            "is_premium_rate": self.is_premium_rate,
            "is_shared_cost": self.is_shared_cost,
            "is_personal_number": self.is_personal_number,
            "is_uan": self.is_uan,
            "is_voicemail": self.is_voicemail,
            "is_pager": self.is_pager,
        }


class PhoneValidator:
    """Validates and parses phone numbers using libphonenumbers."""

    @staticmethod
    def validate(phone_number: str, default_country: Optional[str] = None) -> PhoneValidationResult:
        """
        Parse and validate a phone number.

        Args:
            phone_number: The raw phone number string.
            default_country: ISO country code hint for parsing (e.g. "US", "IN").

        Returns:
            PhoneValidationResult with all available metadata.
        """
        result = PhoneValidationResult()

        try:
            parsed = phonenumbers.parse(phone_number, default_country)
        except phonenumbers.NumberParseException:
            return result

        result.is_valid = phonenumbers.is_valid_number(parsed)
        result.is_possible = phonenumbers.is_possible_number(parsed)

        if not result.is_valid and not result.is_possible:
            return result

        # Basic metadata
        result.country_code = parsed.country_code
        result.national_number = parsed.national_number
        result.extension = parsed.extension if parsed.extension else None

        # Country info
        region = phonenumbers.region_code_for_number(parsed)
        result.country_iso = region

        from phonenumbers.geocoder import country_name_for_number
        result.country_name = country_name_for_number(parsed)

        # Location (geographic region)
        try:
            result.location = ph_geocoder.description_for_number(parsed, "en")
        except Exception:
            result.location = None

        # Carrier
        try:
            result.carrier = ph_carrier.name_for_number(parsed, "en")
        except Exception:
            result.carrier = None

        # Timezones
        try:
            tz_list = ph_timezone.time_zones_for_number(parsed)
            result.timezones = list(tz_list) if tz_list else []
        except Exception:
            result.timezones = []

        # Formatting
        result.formatted_international = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        result.formatted_national = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.NATIONAL
        )
        result.e164 = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )

        # Line type detection
        result.line_type = PhoneValidator._detect_line_type(parsed)
        result.is_mobile = result.line_type == "mobile"
        result.is_fixed_line = result.line_type == "fixed_line"
        result.is_voip = result.line_type == "voip"
        result.is_toll_free = result.line_type == "toll_free"
        result.is_premium_rate = result.line_type == "premium_rate"
        result.is_shared_cost = result.line_type == "shared_cost"
        result.is_personal_number = result.line_type == "personal_number"
        result.is_uan = result.line_type == "uan"
        result.is_voicemail = result.line_type == "voicemail"
        result.is_pager = result.line_type == "pager"

        if result.line_type != "unknown":
            result.is_unknown = False

        return result

    @staticmethod
    def _detect_line_type(parsed) -> str:
        """Detect the line type (mobile, fixed, VoIP, etc.)."""
        from phonenumbers import PhoneNumberType

        num_type = phonenumbers.number_type(parsed)

        type_map = {
            PhoneNumberType.MOBILE: "mobile",
            PhoneNumberType.FIXED_LINE: "fixed_line",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_line_or_mobile",
            PhoneNumberType.VOIP: "voip",
            PhoneNumberType.TOLL_FREE: "toll_free",
            PhoneNumberType.PREMIUM_RATE: "premium_rate",
            PhoneNumberType.SHARED_COST: "shared_cost",
            PhoneNumberType.PERSONAL_NUMBER: "personal_number",
            PhoneNumberType.UAN: "uan",
            PhoneNumberType.VOICEMAIL: "voicemail",
            PhoneNumberType.PAGER: "pager",
        }

        return type_map.get(num_type, "unknown")


# Singleton
phone_validator = PhoneValidator()
