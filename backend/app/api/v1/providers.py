"""Provider connection endpoints — how the settings tab talks to Open Wearables."""

from typing import Any, Dict

import httpx
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.services.ow_client import ow_client

router = APIRouter(prefix="/providers", tags=["providers"])

SUPPORTED = ["whoop", "garmin"]  # Apple Health removed: web backend can't use HealthKit


@router.get("")
async def list_providers() -> Dict[str, Any]:
    """Connection status per provider, as known by Open Wearables."""
    providers = []
    for name in SUPPORTED:
        providers.append({"name": name, "connected": None, "status": "unknown"})
    # TODO: once you see the real response of your OW deployment's
    # connection-status endpoint (check /api/v1/users/{id}/connections or
    # /api/v1/providers in http://localhost:8000/docs), populate `connected`
    # here instead of returning "unknown".
    return {"configured": ow_client.is_configured, "providers": providers}


@router.post("/{name}/connect")
async def connect_provider(name: str) -> Dict[str, Any]:
    if name not in SUPPORTED:
        raise HTTPException(status_code=404, detail=f"Unknown provider '{name}'")
    if not ow_client.is_configured:
        raise HTTPException(status_code=503, detail="Open Wearables is not configured")
    # Frontend redirects the browser to this URL; WHOOP/Garmin consent happens on their site.
    redirect_uri = "http://localhost:3001/settings?connected=" + name
    try:
        url = await ow_client.get_oauth_authorize_url(name, redirect_uri)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"OW error: {exc.response.status_code}") from exc
    if not url:
        raise HTTPException(status_code=502, detail="OW did not return an authorization URL")
    return {"authorization_url": url}


@router.post("/{name}/disconnect")
async def disconnect_provider(name: str) -> Dict[str, str]:
    if name not in SUPPORTED:
        raise HTTPException(status_code=404, detail=f"Unknown provider '{name}'")
    # TODO: call your OW deployment's revoke endpoint (check Swagger at :8000/docs
    # for something like DELETE /api/v1/users/{id}/connections/{provider})
    return {"status": "disconnected", "provider": name}