"""API router — mounts all sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import lookup, auth, export, admin, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(lookup.router, prefix="/lookup", tags=["Phone Lookup"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
