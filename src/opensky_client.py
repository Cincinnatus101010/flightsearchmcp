"""OpenSky upstream client."""

from __future__ import annotations

import httpx

from .config import OPENSKY_BASE

_client: httpx.AsyncClient | None = None


class OpenSkyError(Exception):
    """Raised when an OpenSky Network request fails."""


def _build_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_connections=32, max_keepalive_connections=16),
    )


async def startup_opensky_client() -> None:
    global _client
    if _client is None:
        _client = _build_client()


async def shutdown_opensky_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def fetch_opensky_states(params: dict[str, float]) -> tuple[list[list[object]], int | None]:
    if _client is None:
        await startup_opensky_client()

    assert _client is not None

    try:
        response = await _client.get(f"{OPENSKY_BASE}/states/all", params=params)
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        raise OpenSkyError(f"OpenSky request failed (HTTP {exc.response.status_code}).") from exc
    except httpx.RequestError as exc:
        raise OpenSkyError("Could not reach OpenSky Network.") from exc

    rows = payload.get("states") or []
    upstream_time = payload.get("time")
    return rows, upstream_time
