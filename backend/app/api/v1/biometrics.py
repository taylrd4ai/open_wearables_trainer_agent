"""Biometric data API routes."""

from typing import Any, Dict

from fastapi import APIRouter

from app.services.biometric_services import get_biometric_summary

router = APIRouter(tags=["biometrics"])


@router.get("/biometrics/summary")
async def get_biometric_endpoint(user_id: str = "default") -> Dict[str, Any]:
    """Return biometric summary for a user, falling back to mock data."""
    return await get_biometric_summary(user_id)
