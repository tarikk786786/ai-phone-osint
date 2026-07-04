"""AI investigation service — generates intelligence reports using multiple LLMs."""

from __future__ import annotations

import json
from typing import Any, Optional

import aiohttp
from app.core.config import settings


class AIInvestigationReport:
    """Structured AI-generated investigation report."""

    def __init__(self) -> None:
        self.summary: str = ""
        self.phone_analysis: dict[str, Any] = {}
        self.carrier_analysis: str = ""
        self.geolocation_analysis: str = ""
        self.osint_findings: str = ""
        self.risk_assessment: dict[str, Any] = {}
        self.timeline: list[dict[str, Any]] = []
        self.recommendations: list[str] = []
        self.data_quality_notes: list[str] = []
        self.confidence_level: str = "medium"
        self.model_used: str = "unknown"
        self.disclaimer: str = (
            "This report is AI-generated and based on publicly available information. "
            "All location data is estimated from public telecom databases and should not "
            "be considered real-time GPS tracking. Verify all findings through official channels."
        )

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "phone_analysis": self.phone_analysis,
            "carrier_analysis": self.carrier_analysis,
            "geolocation_analysis": self.geolocation_analysis,
            "osint_findings": self.osint_findings,
            "risk_assessment": self.risk_assessment,
            "timeline": self.timeline,
            "recommendations": self.recommendations,
            "data_quality_notes": self.data_quality_notes,
            "confidence_level": self.confidence_level,
            "model_used": self.model_used,
            "disclaimer": self.disclaimer,
        }


class AIService:
    """Multi-provider AI service for investigation reports."""

    def __init__(self) -> None:
        self.providers = {
            "openai": {
                "api_key": settings.OPENAI_API_KEY,
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-4o-mini",
            },
            "gemini": {
                "api_key": settings.GEMINI_API_KEY,
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
                "model": "gemini-2.0-flash",
            },
            "deepseek": {
                "api_key": settings.DEEPSEEK_API_KEY,
                "endpoint": "https://api.deepseek.com/v1/chat/completions",
                "model": "deepseek-chat",
            },
            "qwen": {
                "api_key": settings.QWEN_API_KEY,
                "endpoint": "https://api.qwen.ai/v1/chat/completions",
                "model": "qwen-max",
            },
            "ollama": {
                "api_key": None,
                "endpoint": f"{settings.OLLAMA_BASE_URL}/v1/chat/completions",
                "model": "llama3.1",
            },
        }

    async def generate_report(
        self,
        phone_data: dict[str, Any],
        osint_data: dict[str, Any],
        geo_data: Optional[dict[str, Any]] = None,
        preferred_provider: str = "auto",
    ) -> AIInvestigationReport:
        """
        Generate an AI investigation report using available LLM providers.

        Args:
            phone_data: Output from PhoneValidator
            osint_data: Output from OSINTService
            geo_data: Optional output from GeolocationService
            preferred_provider: Specific provider or "auto" to try in order

        Returns:
            AIInvestigationReport with structured findings
        """
        prompt = self._build_investigation_prompt(phone_data, osint_data, geo_data)

        # Try providers in order
        provider_order = ["openai", "gemini", "deepseek", "qwen", "ollama"]
        if preferred_provider != "auto" and preferred_provider in self.providers:
            provider_order.insert(0, preferred_provider)

        for provider_name in provider_order:
            provider = self.providers[provider_name]
            if provider_name == "ollama" or provider.get("api_key"):
                try:
                    report = await self._call_provider(provider, prompt, provider_name)
                    if report:
                        return report
                except Exception:
                    continue

        # Fallback: generate a basic report without AI
        return self._generate_fallback_report(phone_data, osint_data, geo_data)

    def _build_investigation_prompt(
        self,
        phone_data: dict[str, Any],
        osint_data: dict[str, Any],
        geo_data: Optional[dict[str, Any]] = None,
    ) -> str:
        """Build the investigation prompt with structured data."""
        return f"""You are an expert OSINT analyst and phone intelligence investigator.

Analyze the following phone number intelligence data and generate a structured investigation report.

**CRITICAL RULES:**
1. Never claim to determine someone's real-time GPS location from a phone number.
2. Clearly label all data as: Verified Data, Estimated Data, Public Data, or AI Inference.
3. Any location information is from public telecom databases (area code, carrier region) only.
4. Include a disclaimer about the limitations of phone number intelligence.

## Phone Validation Data
```json
{json.dumps(phone_data, indent=2)}
```

## OSINT Data
```json
{json.dumps(osint_data, indent=2)}
```

{f"## Geolocation Data\n```json\n{json.dumps(geo_data, indent=2)}\n```" if geo_data else ""}

Generate a response with these sections:
1. **Executive Summary** — Brief overview of findings
2. **Phone Analysis** — Validate number, detect country, region, carrier, line type
3. **Carrier Analysis** — Carrier details, line type, porting status
4. **Geolocation Analysis** — Estimated location (from area code, carrier region — NOT GPS)
5. **OSINT Findings** — Public information gathered
6. **Risk Assessment** — Spam score, fraud indicators, confidence level
7. **Evidence Timeline** — Chronological order of findings
8. **Recommendations** — Next steps for investigation

Format as JSON with keys: summary, phone_analysis (object), carrier_analysis (str), geolocation_analysis (str), osint_findings (str), risk_assessment (object with score, level, factors), timeline (array of objects with date, event, source), recommendations (array of strings), data_quality_notes (array of strings), confidence_level (str)."""

    async def _call_provider(
        self,
        provider: dict[str, Any],
        prompt: str,
        provider_name: str,
    ) -> Optional[AIInvestigationReport]:
        """Call an LLM provider and parse the response."""
        headers = {"Content-Type": "application/json"}
        if provider.get("api_key"):
            if provider_name == "gemini":
                headers["x-goog-api-key"] = provider["api_key"]
            else:
                headers["Authorization"] = f"Bearer {provider['api_key']}"

        payload = {
            "model": provider["model"],
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert OSINT analyst. Respond in JSON format only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                provider["endpoint"],
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    if not content and provider_name == "gemini":
                        content = (
                            data.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )

                    if content:
                        return self._parse_report(content, provider_name)

        return None

    def _parse_report(self, content: str, model: str) -> AIInvestigationReport:
        """Parse AI JSON response into structured report."""
        report = AIInvestigationReport()
        report.model_used = model

        # Try to extract JSON from the response
        try:
            # Find JSON in the response (in case it has markdown wrapping)
            import re
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                data = json.loads(content)

            report.summary = data.get("summary", "")
            report.phone_analysis = data.get("phone_analysis", {})
            report.carrier_analysis = data.get("carrier_analysis", "")
            report.geolocation_analysis = data.get("geolocation_analysis", "")
            report.osint_findings = data.get("osint_findings", "")
            report.risk_assessment = data.get("risk_assessment", {})
            report.timeline = data.get("timeline", [])
            report.recommendations = data.get("recommendations", [])
            report.data_quality_notes = data.get("data_quality_notes", [])
            report.confidence_level = data.get("confidence_level", "medium")

        except (json.JSONDecodeError, AttributeError):
            # Fallback: store raw content as summary
            report.summary = content

        return report

    def _generate_fallback_report(
        self,
        phone_data: dict[str, Any],
        osint_data: dict[str, Any],
        geo_data: Optional[dict[str, Any]] = None,
    ) -> AIInvestigationReport:
        """Generate a basic report without AI when no API keys are available."""
        report = AIInvestigationReport()
        report.model_used = "rule-based-fallback"
        report.confidence_level = "low"

        is_valid = phone_data.get("is_valid", False)
        country = phone_data.get("country_name", "Unknown")
        carrier = phone_data.get("carrier", "Unknown")
        line_type = phone_data.get("line_type", "Unknown")
        location = phone_data.get("location", "Unknown")

        report.summary = (
            f"Phone number is {'valid' if is_valid else 'invalid'}. "
            f"Country: {country}. "
            f"Carrier: {carrier}. "
            f"Line type: {line_type}. "
            f"Estimated region: {location}."
        )
        report.phone_analysis = phone_data
        report.carrier_analysis = f"Carrier: {carrier}, Line Type: {line_type}"
        report.geolocation_analysis = f"Estimated location based on area code: {location}"
        report.osint_findings = json.dumps(osint_data)
        report.risk_assessment = {
            "score": osint_data.get("spam_score", 0),
            "level": "high" if osint_data.get("spam_risk") else "low",
            "factors": osint_data.get("spam_sources", []),
        }
        report.recommendations = [
            "Configure an LLM API key (OpenAI, Gemini, or DeepSeek) for AI-enhanced reports",
            "Verify carrier information through official telecom databases",
            "Cross-reference with additional public sources",
        ]
        report.data_quality_notes = [
            "All location data is estimated from area codes and public telecom databases",
            "No real-time GPS tracking data is used or available",
            "Carrier information may be affected by number portability",
        ]

        return report


ai_service = AIService()
