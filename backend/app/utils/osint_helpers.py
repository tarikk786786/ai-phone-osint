"""OSINT helper functions — web scraping, data extraction utilities."""

from __future__ import annotations

import json
import re
from typing import Any, Optional


def extract_phone_numbers(text: str) -> list[str]:
    """Extract phone numbers from arbitrary text using regex patterns."""
    patterns = [
        r"\+?1?\d{10,15}",  # Basic international
        r"\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # US format
        r"\+\d{1,3}\s?\d{6,14}",  # E.164-like
    ]

    numbers: list[str] = []
    for pattern in patterns:
        found = re.findall(pattern, text)
        numbers.extend(found)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique = []
    for n in numbers:
        if n not in seen:
            seen.add(n)
            unique.append(n)

    return unique


def parse_breach_data(raw: str) -> list[dict[str, Any]]:
    """Parse breach data from text responses."""
    breaches: list[dict[str, Any]] = []
    # Look for structured data patterns
    if raw.startswith("[") or raw.startswith("{"):
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return [data]
        except json.JSONDecodeError:
            pass

    # Fallback: line-by-line parsing
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        breaches.append({"raw": line, "source": "unknown"})

    return breaches


# Known public caller ID / spam report sources
PUBLIC_SOURCES = {
    "spamcalls.net": "https://www.spamcalls.net/en/lookup/{}",
    "spamnumber.com": "https://spamnumber.com/lookup/{}",
    "callercenter.com": "https://www.callercenter.com/{}",
    "whitepages": "https://www.whitepages.com/phone/{}",
    "yellowpages": "https://www.yellowpages.com/phone-lookup/{}",
    "anywho": "https://www.anywho.com/phone/{}",
}


def get_public_source_urls(phone: str) -> list[dict[str, str]]:
    """Generate public source lookup URLs for a phone number."""
    urls = []
    for name, template in PUBLIC_SOURCES.items():
        # Clean phone number for URL formatting
        clean_phone = re.sub(r"[^\d]", "", phone)
        if clean_phone.startswith("1") and len(clean_phone) == 11:
            clean_phone = clean_phone[1:]
        url = template.format(clean_phone)
        urls.append({"name": name, "url": url})
    return urls
