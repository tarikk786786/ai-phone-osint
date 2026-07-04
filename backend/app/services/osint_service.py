"""OSINT intelligence service - enhanced public data gathering from 15+ sources."""

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
        self.spam_details: list[dict[str, Any]] = []
        self.breaches: list[dict[str, Any]] = []
        self.social_media: list[dict[str, Any]] = []
        self.associated_names: list[str] = []
        self.associated_emails: list[str] = []
        self.associated_addresses: list[dict[str, Any]] = []
        self.public_reports: list[str] = []
        self.whois_info: Optional[dict[str, Any]] = None
        self.source_count: int = 0
        self.reputation: Optional[str] = None
        self.caller_type: Optional[str] = None
        self.location_intel: list[dict[str, Any]] = []
        self.data_breach_count: int = 0
        self.dark_web_mentions: int = 0

    def to_dict(self) -> dict:
        return {
            "spam_risk": self.spam_risk,
            "spam_score": self.spam_score,
            "spam_sources": self.spam_sources,
            "spam_details": self.spam_details,
            "breaches": self.breaches,
            "social_media": self.social_media,
            "associated_names": self.associated_names,
            "associated_emails": self.associated_emails,
            "associated_addresses": self.associated_addresses,
            "public_reports": self.public_reports,
            "whois_info": self.whois_info,
            "source_count": self.source_count,
            "reputation": self.reputation,
            "caller_type": self.caller_type,
            "location_intel": self.location_intel,
            "data_breach_count": self.data_breach_count,
            "dark_web_mentions": self.dark_web_mentions,
        }


class OSINTService:
    """Gathers publicly available intelligence about a phone number from 15+ sources."""

    SOCIAL_PLATFORMS = [
        "whatsapp", "telegram", "signal", "viber",
        "facebook", "instagram", "twitter",
        "linkedin", "tiktok", "snapchat",
    ]

    async def investigate(self, phone_number: str, e164: str) -> OSINTResult:
        """Run OSINT checks across multiple public sources in parallel."""
        result = OSINTResult()

        checks = [
            self._check_spam_databases(phone_number),
            self._check_social_media_presence(phone_number, e164),
            self._search_public_breaches(phone_number),
            self._search_public_reports(phone_number),
            self._check_caller_id_databases(phone_number),
            self._check_number_reputation(phone_number),
        ]

        outcomes = await asyncio.gather(*checks, return_exceptions=True)

        spam_data, social_data, breach_data, report_data, caller_data, reputation_data = (
            outcomes[:6] if len(outcomes) >= 6 else outcomes + [None] * (6 - len(outcomes))
        )

        if isinstance(spam_data, dict):
            result.spam_risk = spam_data.get("is_spam")
            result.spam_score = spam_data.get("score")
            result.spam_sources = spam_data.get("sources", [])
            result.spam_details = spam_data.get("details", [])

        if isinstance(social_data, list):
            result.social_media = social_data

        if isinstance(breach_data, list):
            result.breaches = breach_data
            result.data_breach_count = len(breach_data)

        if isinstance(report_data, list):
            result.public_reports = report_data

        if isinstance(caller_data, dict):
            result.caller_type = caller_data.get("type")
            result.location_intel = caller_data.get("locations", [])

        if isinstance(reputation_data, dict):
            result.reputation = reputation_data.get("reputation")
            result.spam_score = reputation_data.get("score", result.spam_score)

        result.source_count = (
            len(result.spam_sources)
            + len(result.social_media)
            + len(result.breaches)
            + len(result.public_reports)
        )

        return result

    async def _check_spam_databases(self, phone: str) -> dict:
        """Check public spam/telemarketer databases - 8+ sources."""
        found_sources: list[str] = []
        found_details: list[dict[str, Any]] = []
        total_score = 0

        spam_sources_config = [
            {"name": "spamcalls.net", "url": f"https://www.spamcalls.net/en/lookup/{phone}"},
            {"name": "spamnumber.com", "url": f"https://spamnumber.com/lookup/{phone}"},
            {"name": "who-called.me", "url": f"https://who-called.me/{phone}"},
            {"name": "callersmart.com", "url": f"https://www.callersmart.com/phone-number/{phone}"},
            {"name": "truecaller.com", "url": f"https://www.truecaller.com/search/{phone}"},
            {"name": "shouldianswer.net", "url": f"https://shouldianswer.net/number/{phone}"},
            {"name": "tellows.com", "url": f"https://www.tellows.com/num/{phone}"},
            {"name": "888notes.com", "url": f"https://888notes.com/{phone}"},
        ]

        async def check_source(source: dict) -> Optional[dict]:
            """Check a single spam database. Returns match data or None."""
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        source["url"],
                        timeout=aiohttp.ClientTimeout(total=8),
                        headers={"User-Agent": "Mozilla/5.0 (compatible; PhoneOSINT/1.0)"},
                    ) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            spam_keywords = [
                                "spam", "scam", "fraud", "telemarketer", "harassment",
                                "robocall", "unwanted", "blocked", "complaint", "reported",
                                "dangerous", "suspicious", "annoying",
                            ]
                            matches = [kw for kw in spam_keywords if kw in text.lower()]
                            if matches:
                                return {
                                    "source": source["name"],
                                    "score_delta": min(15 * len(matches), 40),
                                    "keywords": matches[:5],
                                    "url": source["url"],
                                }
            except Exception:
                pass
            return None

        tasks = [check_source(s) for s in spam_sources_config]
        results = await asyncio.gather(*tasks)

        for r in results:
            if r is not None:
                found_sources.append(r["source"])
                total_score += r["score_delta"]
                found_details.append({
                    "source": r["source"],
                    "keywords_found": r["keywords"],
                    "url": r["url"],
                })

        is_spam = len(found_sources) > 0
        final_score = min(total_score, 100) if is_spam else 0

        return {"is_spam": is_spam, "score": final_score, "sources": found_sources, "details": found_details}

    async def _check_social_media_presence(self, phone: str, e164: str) -> list[dict]:
        """Check if phone number is associated with social media (public)."""
        phone_clean = e164.lstrip("+")

        platforms = {
            "whatsapp": f"https://wa.me/{phone_clean}",
            "telegram": f"https://t.me/+{phone_clean}",
            "signal": f"https://signal.me/#p/+{phone_clean}",
            "viber": f"viber://chat?number=%2B{phone_clean}",
            "facebook": f"https://www.facebook.com/search/people/?q={phone_clean}",
            "instagram": f"https://www.instagram.com/accounts/login/?next=/explore/search/keyword/?q={phone_clean}",
            "twitter": f"https://twitter.com/search?q={phone_clean}",
            "linkedin": f"https://www.linkedin.com/search/results/all/?keywords={phone_clean}",
            "tiktok": f"https://www.tiktok.com/search?q={phone_clean}",
            "snapchat": f"https://www.snapchat.com/add/{phone_clean}",
        }

        async def check_platform(platform: str, url: str) -> dict:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=5),
                        allow_redirects=False,
                        headers={"User-Agent": "Mozilla/5.0"},
                    ) as resp:
                        return {
                            "platform": platform,
                            "url": url,
                            "found": resp.status in (200, 302),
                            "status_code": resp.status,
                            "public": True,
                        }
            except Exception:
                return {
                    "platform": platform,
                    "url": url,
                    "found": False,
                    "public": True,
                    "error": "Connection failed",
                }

        tasks = [check_platform(p, u) for p, u in platforms.items()]
        results = await asyncio.gather(*tasks)
        return list(results)

    async def _search_public_breaches(self, phone: str) -> list[dict]:
        """Search for phone number in public breach databases."""
        breaches = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{phone}",
                    headers={"User-Agent": "PhoneOSINT-Research"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for breach in data:
                            breaches.append({
                                "source": "haveibeenpwned",
                                "name": breach.get("Name"),
                                "title": breach.get("Title"),
                                "date": breach.get("BreachDate"),
                                "data_classes": breach.get("DataClasses", []),
                            })
        except Exception:
            pass

        return breaches

    async def _search_public_reports(self, phone: str) -> list[str]:
        """Search for public reports/caller ID information."""
        search_urls = [
            f"https://www.whitepages.com/phone/{phone}",
            f"https://www.yellowpages.com/phone-lookup/{phone}",
            f"https://www.thatsthem.com/phone/{phone}",
            f"https://www.spydialer.com/default.aspx?r={phone.lstrip('+')}",
        ]

        async def check_url(url: str) -> Optional[str]:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=8),
                        headers={"User-Agent": "Mozilla/5.0"},
                    ) as resp:
                        if resp.status == 200:
                            return url
            except Exception:
                pass
            return None

        tasks = [check_url(u) for u in search_urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def _check_caller_id_databases(self, phone: str) -> dict:
        """Check caller ID databases for caller type and location intel."""
        result: dict[str, Any] = {"type": None, "locations": []}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://www.numverify.com/php/phonenumbers.php?number={phone}&country=&limit=10&format=1",
                    timeout=aiohttp.ClientTimeout(total=8),
                    headers={"User-Agent": "Mozilla/5.0"},
                ) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if "business" in text.lower():
                            result["type"] = "business"
                        elif "mobile" in text.lower():
                            result["type"] = "mobile"
                        elif "landline" in text.lower():
                            result["type"] = "landline"
        except Exception:
            pass

        return result

    async def _check_number_reputation(self, phone: str) -> dict:
        """Check number reputation across multiple scoring services."""
        score = 0
        reputation = "unknown"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.ipqualityscore.com/phone/{phone}",
                    timeout=aiohttp.ClientTimeout(total=8),
                ) as resp:
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                        except Exception:
                            return {"reputation": reputation, "score": score}
                        if data.get("fraud_score"):
                            score = data["fraud_score"]
                            if score >= 75:
                                reputation = "high_risk"
                            elif score >= 50:
                                reputation = "medium_risk"
                            elif score >= 25:
                                reputation = "low_risk"
                            else:
                                reputation = "clean"
        except Exception:
            pass

        return {"reputation": reputation, "score": score}

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
