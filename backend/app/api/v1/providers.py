"""Provider connection endpoints — how the settings tab talks to Open Wearables."""

from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, HTTPException

from app.services.ow_client import ow_client

router = APIRouter(prefix="/providers", tags=["providers"])

SUPPORTED: List[str] = ["whoop", "garmin"]  # Apple Health removed: web backend can't use HealthKit


@router.get("")
async def list_providers() -> Dict[str, Any]:
    """Connection status per provider, as known by Open Wearables."""
    if not ow_client.is_configured:
        providers = [{"name": name, "connected": False, "status": "ow_not_configured"} for name in SUPPORTED]
        return {"configured": False, "providers": providers}

    try:
        connections = await ow_client.get_connections()
    except httpx.HTTPStatusError as exc:
        providers = [{"name": name, "connected": None, "status": f"ow_error_{exc.response.status_code}"} for name in SUPPORTED]
        return {"configured": True, "providers": providers}

    by_provider: Dict[str, Dict[str, Any]] = {}
    if isinstance(connections, list):
        for conn in connections:
            provider = conn.get("provider")
            status = conn.get("status")
            if provider:
                by_provider[provider] = {"connected": status == "active", "status": status}

    providers = []
    for name in SUPPORTED:
        meta = by_provider.get(name, {"connected": False, "status": "not_connected"})
        providers.append({"name": name, **meta})

    return {"configured": True, "providers": providers}


@router.post("/{name}/connect")
async def connect_provider(name: str) -> Dict[str, Any]:
    if name not in SUPPORTED:
        raise HTTPException(status_code=404, detail=f"Unknown provider '{name}'")
    if not ow_client.is_configured:
        raise HTTPException(status_code=503, detail="Open Wearables is not configured")
    redirect_uri = f"http://localhost:3001/settings?connected={name}"
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
    if not ow_client.is_configured:
        raise HTTPException(status_code=503, detail="Open Wearables is not configured")
    try:
        await ow_client.revoke_connection(name)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"OW error: {exc.response.status_code}") from exc
    return {"status": "disconnected", "provider": name}