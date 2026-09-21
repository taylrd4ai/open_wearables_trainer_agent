"""High-level data accessors backed by Open Wearables.

This module is the single place where the trainer app pulls workouts,
sleep, scores, and timeseries from Open Wearables. Routers should call
these functions rather than talking to OW directly.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from app.services.ow_client import ow_client


async def fetch_workouts(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Return a list of unified workout events for the configured user."""
    start = start_date.isoformat() if start_date else None
    end = end_date.isoformat() if end_date else None
    return await ow_client.get_workouts(start_date=start, end_date=end, limit=limit)


async def fetch_sleep_sessions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 14,
) -> List[Dict[str, Any]]:
    """Return sleep events (sessions) for the configured user."""
    start = start_date.isoformat() if start_date else None
    end = end_date.isoformat() if end_date else None
    return await ow_client.get_sleep_events(start_date=start, end_date=end, limit=limit)


async def fetch_sleep_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Return daily sleep summaries (duration, efficiency, etc.)."""
    start = start_date.isoformat() if start_date else None
    end = end_date.isoformat() if end_date else None
    return await ow_client.get_sleep_summary(start_date=start, end_date=end)


async def fetch_health_scores(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Return health scores such as Sleep Score and Resilience Score."""
    start = start_date.isoformat() if start_date else None
    end = end_date.isoformat() if end_date else None
    return await ow_client.get_health_scores(start_date=start, end_date=end)


async def fetch_timeseries(
    types: List[str],
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    resolution: str = "1day",
) -> List[Dict[str, Any]]:
    """Return timeseries samples for supported providers (non-Whoop).

    For Whoop, prefer recovery / health scores + events over timeseries.
    """
    return await ow_client.get_timeseries(
        types=types, start_time=start_time, end_time=end_time, resolution=resolution
    )
