"""Export service — generates PDF, CSV, and JSON exports."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any, Optional
from weasyprint import HTML


class ExportService:
    """Generate export files in multiple formats."""

    @staticmethod
    def to_json(data: dict[str, Any], pretty: bool = True) -> str:
        """Serialize data to JSON string."""
        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)

    @staticmethod
    def to_csv(data: list[dict[str, Any]]) -> str:
        """Serialize list of dicts to CSV string."""
        if not data:
            return ""

        output = io.StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    @staticmethod
    def to_pdf(
        report_data: dict[str, Any],
        template: Optional[str] = None,
    ) -> bytes:
        """
        Generate a PDF report from investigation data.

        Args:
            report_data: The full investigation data to include in the PDF
            template: Optional HTML template string. Uses default if None.

        Returns:
            PDF as bytes
        """
        html_content = template or ExportService._default_template(report_data)
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes

    @staticmethod
    def _default_template(data: dict[str, Any]) -> str:
        """Generate a default HTML template for PDF export."""
        phone = data.get("phone_data", {})
        osint = data.get("osint_data", {})
        report = data.get("ai_report", {})

        # Format timeline
        timeline_html = ""
        for item in report.get("timeline", []):
            timeline_html += f"""
            <tr>
                <td style="padding: 6px 12px; border-bottom: 1px solid #ddd;">{item.get('date', 'N/A')}</td>
                <td style="padding: 6px 12px; border-bottom: 1px solid #ddd;">{item.get('event', 'N/A')}</td>
                <td style="padding: 6px 12px; border-bottom: 1px solid #ddd;">{item.get('source', 'N/A')}</td>
            </tr>"""

        risk = report.get("risk_assessment", {})
        recommendations = report.get("recommendations", [])

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Phone Intelligence Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #222; }}
        h1 {{ color: #1a56db; border-bottom: 2px solid #1a56db; padding-bottom: 10px; }}
        h2 {{ color: #374151; margin-top: 30px; }}
        .meta {{ color: #6B7280; font-size: 14px; margin-bottom: 20px; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .data-table th {{ background: #F3F4F6; text-align: left; padding: 8px 12px; border-bottom: 2px solid #ddd; }}
        .data-table td {{ padding: 8px 12px; border-bottom: 1px solid #eee; }}
        .risk-high {{ color: #DC2626; font-weight: bold; }}
        .risk-medium {{ color: #F59E0B; font-weight: bold; }}
        .risk-low {{ color: #10B981; font-weight: bold; }}
        .recommendation {{ background: #F3F4F6; padding: 12px; margin: 8px 0; border-radius: 6px; }}
        .disclaimer {{ margin-top: 40px; padding: 16px; background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; font-size: 12px; color: #991B1B; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #9CA3AF; text-align: center; }}
    </style>
</head>
<body>
    <h1>AI Phone Intelligence Report</h1>
    <div class="meta">
        <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}<br>
        <strong>Phone:</strong> {phone.get('e164', phone.get('raw_input', 'N/A'))}<br>
        <strong>AI Model:</strong> {report.get('model_used', 'N/A')}<br>
        <strong>Confidence:</strong> {report.get('confidence_level', 'N/A')}
    </div>

    <h2>Executive Summary</h2>
    <p>{report.get('summary', 'No summary available.')}</p>

    <h2>Phone Validation</h2>
    <table class="data-table">
        <tr><th>Property</th><th>Value</th></tr>
        <tr><td>Valid</td><td>{'Yes' if phone.get('is_valid') else 'No'}</td></tr>
        <tr><td>Country</td><td>{phone.get('country_name', 'N/A')} ({phone.get('country_iso', 'N/A')})</td></tr>
        <tr><td>Location</td><td>{phone.get('location', 'N/A')}</td></tr>
        <tr><td>Carrier</td><td>{phone.get('carrier', 'N/A')}</td></tr>
        <tr><td>Line Type</td><td>{phone.get('line_type', 'N/A')}</td></tr>
        <tr><td>Timezone(s)</td><td>{', '.join(phone.get('timezones', [])) or 'N/A'}</td></tr>
        <tr><td>International Format</td><td>{phone.get('formatted_international', 'N/A')}</td></tr>
    </table>

    <h2>Risk Assessment</h2>
    <table class="data-table">
        <tr><th>Factor</th><th>Value</th></tr>
        <tr><td>Risk Score</td><td class="risk-{risk.get('level', 'low')}">{risk.get('score', 'N/A')}/100</td></tr>
        <tr><td>Risk Level</td><td class="risk-{risk.get('level', 'low')}">{risk.get('level', 'Unknown').upper()}</td></tr>
        <tr><td>Spam Risk</td><td>{'Yes' if osint.get('spam_risk') else 'No'}</td></tr>
    </table>

    <h2>OSINT Findings</h2>
    <p>{report.get('osint_findings', 'No OSINT findings available.')}</p>

    <h2>Evidence Timeline</h2>
    <table class="data-table">
        <tr><th>Date</th><th>Event</th><th>Source</th></tr>
        {timeline_html or '<tr><td colspan="3" style="text-align:center; color:#999;">No timeline data available.</td></tr>'}
    </table>

    <h2>Recommendations</h2>
    {' '.join(f'<div class="recommendation">• {rec}</div>' for rec in recommendations) or '<p>No recommendations.</p>'}

    <div class="disclaimer">
        <strong>⚠️ Disclaimer:</strong> {report.get('disclaimer', 'This report is AI-generated and based on publicly available and estimated data.')}
    </div>

    <div class="footer">
        Generated by AI Phone Intelligence OSINT Platform v1.0<br>
        Not for use in real-time surveillance or tracking.
    </div>
</body>
</html>"""


export_service = ExportService()
