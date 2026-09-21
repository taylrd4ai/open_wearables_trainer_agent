"""Thin client for the Open Wearables platform API."""

from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class OpenWearablesClient:
    """Wrapper around the Open Wearables REST API.

    OW owns provider OAuth, token storage, and polling; we just
    pull normalized data for our configured user.
    """

    def __init__(self) -> None:
        self.base_url = settings.OPEN_WEARABLES_BASE_URL.rstrip("/")
        self.user_id = settings.OPEN_WEARABLES_USER_ID
        self._headers = {"X-Open-Wearables-API-Key": settings.OPEN_WEARABLES_API_KEY}

    @property
    def is_configured(self) -> bool:
        return bool(settings.OPEN_WEARABLES_API_KEY and settings.OPEN_WEARABLES_USER_ID)

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Internal GET helper.

        - Handles repeated list params (e.g. types=a&types=b).
        - Unwraps OW's { "data": [...] } envelope by default.
        """
        query: List[tuple] = []
        for key, value in (params or {}).items():
            if isinstance(value, list):
                query.extend((key, v) for v in value)
            elif value is not None:
                query.append((key, str(value)))

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._headers,
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            resp = await client.get(path, params=query)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data

    async def _delete(self, path: str) -> Any:
        """Internal DELETE helper."""
        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._headers,
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            resp = await client.delete(path)
            resp.raise_for_status()
            if resp.content:
                return resp.json()
            return {"status": "ok"}

    async def get_timeseries(
        self,
        types: List[str],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        resolution: str = "1day",
    ) -> Any:
        """Fetch normalized timeseries for the configured user.

        Matches OW external API: /api/v1/users/{user_id}/timeseries.
        """
        return await self._get(
            f"/api/v1/users/{self.user_id}/timeseries",
            params={
                "types": types,
                "resolution": resolution,
                "start_time": start_time,
                "end_time": end_time,
            },
        )

    async def get_workouts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
    ) -> Any:
        """Fetch workout events from OW.

        Uses unified events endpoint: /api/v1/users/{user_id}/events/workouts.
        """
        return await self._get(
            f"/api/v1/users/{self.user_id}/events/workouts",
            params={"start_date": start_date, "end_date": end_date, "limit": limit},
        )

    async def get_sleep_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 14,
    ) -> Any:
        """Fetch sleep events (sessions) from OW."""
        return await self._get(
            f"/api/v1/users/{self.user_id}/events/sleep",
            params={"start_date": start_date, "end_date": end_date, "limit": limit},
        )

    async def get_sleep_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Any:
        """Fetch daily sleep summaries for the user."""
        return await self._get(
            f"/api/v1/users/{self.user_id}/summaries/sleep",
            params={"start_date": start_date, "end_date": end_date},
        )

    async def get_health_scores(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Any:
        """Fetch health scores (Sleep Score, Resilience Score, Recovery) from OW."""
        return await self._get(
            f"/api/v1/users/{self.user_id}/health-scores",
            params={"start_date": start_date, "end_date": end_date},
        )

    async def get_connections(self) -> Any:
        """Return provider connections for the configured user."""
        return await self._get(f"/api/v1/users/{self.user_id}/connections")

    async def revoke_connection(self, provider: str) -> Any:
        """Disconnect a provider for the configured user."""
        return await self._delete(
            f"/api/v1/users/{self.user_id}/connections/{provider}"
        )

    async def get_oauth_authorize_url(
        self, provider: str, redirect_uri: str
    ) -> Optional[str]:
        """Get the authorization URL for a provider via OW's OAuth endpoints."""
        data = await self._get(
            f"/api/v1/oauth/{provider}/authorize",
            params={"user_id": self.user_id, "redirect_uri": redirect_uri},
        )
        if isinstance(data, dict):
            return data.get("authorization_url")
        return None


ow_client = OpenWearablesClient()
