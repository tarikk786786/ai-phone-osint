"""OSINT intelligence service — public data gathering from multiple sources."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Optional

import aiohttp


class OSINTResult:
    """Aggregated OSINT intelligence for a phone number."""

    def __init__(self) -> None:
        self.spam_risk: Optional[bool] = None
        self.spam_score: Optional[int] = None
        self.spam_sources: list[str] = []
        self.breaches: list[dict[str, Any]] = []
        self.social_media: list[dict[str, Any]] = []
        self.associated_names: list[str] = []
        self.associated_emails: list[str] = []
        self.associated_addresses: list[dict[str, Any]] = []
        self.public_reports: list[str] = []
        self.whois_info: Optional[dict[str, Any]] = None
        self.source_count: int = 0

    def to_dict(self) -> dict:
        return {
            "spam_risk": self.spam_risk,
            "spam_score": self.spam_score,
            "spam_sources": self.spam_sources,
            "breaches": self.breaches,
            "social_media": self.social_media,
            "associated_names": self.associated_names,
            "associated_emails": self.associated_emails,
            "associated_addresses": self.associated_addresses,
            "public_reports": self.public_reports,
            "whois_info": self.whois_info,
            "source_count": self.source_count,
        }


class OSINTService:
    """Gathers publicly available intelligence about a phone number."""

    SPAM_DATABASES = [
        "https://phone.cncta.net/api/check",
        "https://www.spamcalls.net/api/lookup",
    ]

    SOCIAL_PLATFORMS = [
        "whatsapp", "telegram", "signal", "viber",
        "facebook", "instagram", "twitter",
    ]

    async def investigate(self, phone_number: str, e164: str) -> OSINTResult:
        """
        Run OSINT checks across multiple public sources.

        This does NOT access private data. Only public, lawful sources.
        """
        result = OSINTResult()

        checks = [
            self._check_spam_databases(phone_number),
            self._check_social_media_presence(phone_number, e164),
            self._search_public_breaches(phone_number),
            self._search_public_reports(phone_number),
        ]

        outcomes = await asyncio.gather(*checks, return_exceptions=True)

        spam_data, social_data, breach_data, report_data = outcomes[:4]

        if isinstance(spam_data, dict):
            result.spam_risk = spam_data.get("is_spam")
            result.spam_score = spam_data.get("score")
            result.spam_sources = spam_data.get("sources", [])

        if isinstance(social_data, list):
            result.social_media = social_data

        if isinstance(breach_data, list):
            result.breaches = breach_data

        if isinstance(report_data, list):
            result.public_reports = report_data

        result.source_count = len(result.spam_sources) + len(result.social_media)

        return result

    async def _check_spam_databases(self, phone: str) -> dict:
        """Check public spam/telemarketer databases."""
        sources = []
        is_spam = False
        score = 0

        # Use web scraping / API calls to spam databases
        # This is a simulated check — real implementation would use actual APIs
        spam_sources_config = [
            {"name": "spamcalls.net", "url": f"https://www.spamcalls.net/en/lookup/{phone}"},
            {"name": "spamnumber.com", "url": f"https://spamnumber.com/lookup/{phone}"},
        ]

        for source in spam_sources_config:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        source["url"],
                        timeout=aiohttp.ClientTimeout(total=10),
                        headers={"User-Agent": "Mozilla/5.0"},
                    ) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            # Basic heuristic: check for spam-related keywords
                            spam_keywords = ["spam", "scam", "fraud", "telemarketer", "harassment"]
                            if any(kw in text.lower() for kw in spam_keywords):
                                sources.append(source["name"])
                                score += 25
            except Exception:
                continue

        if len(sources) > 0:
            is_spam = True
            score = min(score, 100)

        return {"is_spam": is_spam, "score": score, "sources": sources}

    async def _check_social_media_presence(self, phone: str, e164: str) -> list[dict]:
        """Check if phone number is associated with social media (publicly)."""
        results = []
        platforms = {
            "whatsapp": f"https://wa.me/{e164.lstrip('+')}",
            "telegram": f"https://t.me/+{e164.lstrip('+')}",
            "signal": f"https://signal.me/#p/+{e164.lstrip('+')}",
        }

        for platform, url in platforms.items():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=5),
                        allow_redirects=False,
                    ) as resp:
                        # A 200 or 302 suggests the platform recognizes the number
                        if resp.status in (200, 302):
                            results.append({
                                "platform": platform,
                                "url": url,
                                "found": True,
                                "public": True,
                            })
                        else:
                            results.append({
                                "platform": platform,
                                "url": url,
                                "found": False,
                                "public": True,
                            })
            except Exception:
                results.append({
                    "platform": platform,
                    "url": url,
                    "found": False,
                    "public": True,
                    "error": "Connection failed",
                })

        return results

    async def _search_public_breaches(self, phone: str) -> list[dict]:
        """Search for phone number in public breach databases."""
        # Uses public breach data — not private databases
        # Real implementation would integrate with services like Have I Been Pwned API
        return []

    async def _search_public_reports(self, phone: str) -> list[str]:
        """Search for public reports/caller ID information."""
        reports = []
        search_urls = [
            f"https://www.yellowpages.com/phone-lookup/{phone}",
            f"https://www.whitepages.com/phone/{phone}",
        ]

        for url in search_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=10),
                        headers={"User-Agent": "Mozilla/5.0"},
                    ) as resp:
                        if resp.status == 200:
                            reports.append(url)
            except Exception:
                continue

        return reports

    async def whois_lookup(self, domain: str) -> Optional[dict]:
        """Perform a WHOIS lookup on a domain."""
        try:
            import whois
            w = whois.query(domain)
            if w:
                return {
                    "domain": w.name,
                    "registrar": w.registrar,
                    "creation_date": str(w.creation_date),
                    "expiration_date": str(w.expiration_date),
                    "name_servers": w.name_servers,
                    "organization": w.org,
                    "country": w.country,
                }
        except ImportError:
            pass
        except Exception:
            pass

        return None


osint_service = OSINTService()
