"""Export endpoints — PDF, CSV, JSON downloads."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.phone import PhoneLookup
from app.models.user import User
from app.services.export_service import export_service

router = APIRouter()


@router.get("/json/{lookup_id}")
async def export_json(
    lookup_id: str,
    pretty: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export lookup as JSON."""
    result = await db.execute(
        select(PhoneLookup).where(
            PhoneLookup.id == lookup_id,
            PhoneLookup.user_id == user.id,
        )
    )
    lookup = result.scalar_one_or_none()
    if not lookup:
        raise HTTPException(status_code=404, detail="Lookup not found")

    json_str = export_service.to_json({
        "phone_data": lookup.to_dict(),
        "raw_data": lookup.raw_data or {},
    }, pretty=pretty)

    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=lookup_{lookup_id}.json"},
    )


@router.get("/csv")
async def export_csv(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export all lookups as CSV."""
    result = await db.execute(
        select(PhoneLookup).where(PhoneLookup.user_id == user.id).order_by(PhoneLookup.created_at.desc())
    )
    lookups = result.scalars().all()
    records = [l.to_dict() for l in lookups]

    csv_str = export_service.to_csv(records)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=phone_lookups.csv"},
    )


@router.get("/pdf/{lookup_id}")
async def export_pdf(
    lookup_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export lookup as PDF report."""
    result = await db.execute(
        select(PhoneLookup).where(
            PhoneLookup.id == lookup_id,
            PhoneLookup.user_id == user.id,
        )
    )
    lookup = result.scalar_one_or_none()
    if not lookup:
        raise HTTPException(status_code=404, detail="Lookup not found")

    phone_data = lookup.to_dict()
    report_data = {
        "phone_data": phone_data,
        "osint_data": {
            "spam_risk": phone_data.get("is_spam_risk"),
            "spam_score": phone_data.get("spam_score"),
        },
        "ai_report": {
            "summary": "Phone intelligence report",
            "risk_assessment": {"score": phone_data.get("risk_score"), "level": "medium"},
            "model_used": phone_data.get("ai_report_id", "N/A"),
            "confidence_level": "medium",
            "timeline": [],
            "recommendations": [],
            "disclaimer": "This report is based on publicly available and estimated data only.",
        },
    }

    pdf_bytes = export_service.to_pdf(report_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{lookup_id}.pdf"},
    )
