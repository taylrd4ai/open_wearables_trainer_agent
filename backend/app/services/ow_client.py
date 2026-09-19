"""Thin client for the Open Wearables platform API."""

from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class OpenWearablesClient:
    """Wrapper around the Open Wearables REST API.

    OW owns provider OAuth, token storage, and polling; we just
    pull normalized data for our user.
    """

    def __init__(self) -> None:
        self.base_url = settings.OPEN_WEARABLES_BASE_URL.rstrip("/")
        self.user_id = settings.OPEN_WEARABLES_USER_ID
        self._headers = {"X-Open-Wearables-API-Key": settings.OPEN_WEARABLES_API_KEY}

    @property
    def is_configured(self) -> bool:
        return bool(settings.OPEN_WEARABLES_API_KEY and settings.OPEN_WEARABLES_USER_ID)

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        # OW uses repeated query params for list filters (e.g. ?types=a&types=b)
        query: List[tuple] = []
        for key, value in (params or {}).items():
            if isinstance(value, list):
                query.extend((key, v) for v in value)
            elif value is not None:
                query.append((key, str(value)))
        async with httpx.AsyncClient(
            base_url=self.base_url, headers=self._headers, timeout=30.0, follow_redirects=True
        ) as client:
            resp = await client.get(path, params=query)
            resp.raise_for_status()
            return resp.json()

    async def get_timeseries(
        self,
        types: List[str],
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        resolution: str = "1day",
    ) -> Any:
        return await self._get(
            "/api/v1/timeseries",
            params={
                "user_id": self.user_id,
                "types": types,
                "resolution": resolution,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
            },
        )

    async def get_workouts(self, limit: int = 50) -> Any:
        return await self._get(f"/api/v1/users/{self.user_id}/workouts", params={"limit": limit})

    async def get_sleep(self, limit: int = 14) -> Any:
        return await self._get(f"/api/v1/users/{self.user_id}/sleep", params={"limit": limit})

    async def get_oauth_authorize_url(self, provider: str, redirect_uri: str) -> Optional[str]:
        data = await self._get(
            f"/api/v1/oauth/{provider}/authorize",
            params={"user_id": self.user_id, "redirect_uri": redirect_uri},
        )
        return data.get("authorization_url") if isinstance(data, dict) else None


ow_client = OpenWearablesClient()