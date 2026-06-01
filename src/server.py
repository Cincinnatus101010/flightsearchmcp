"""MCP server exposing live flight search tools."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .config import CACHE_SECONDS, load_dotenv as load_app_dotenv
from .formatters import (
    format_aircraft_list,
    format_airspace_summary,
    format_search_results,
)
from .lifecycle import shutdown, startup
from .models import AircraftPageResponse, SearchResponse
from .opensky_client import OpenSkyError
from .region import US_BBOX, US_REGION, resolve_bbox
from .service import get_aircraft_page, search_aircraft_in_bbox


def _resolve_bbox_or_message(
    lamin: float | None,
    lomin: float | None,
    lamax: float | None,
    lomax: float | None,
) -> dict[str, float] | str:
    bbox_params = [lamin, lomin, lamax, lomax]
    if any(v is not None for v in bbox_params) and not all(v is not None for v in bbox_params):
        return "Provide all bounding box params (lamin, lomin, lamax, lomax) or none for CONUS."

    try:
        params = resolve_bbox(lamin, lomin, lamax, lomax)
    except ValueError as exc:
        return str(exc)

    if params is None:
        return "Bounding box does not intersect the continental US region."

    return params


def _page_payload(response: AircraftPageResponse) -> dict:
    data = response.model_dump()
    data["aircraft"] = [ac.model_dump() for ac in response.aircraft]
    return data


def _search_payload(response: SearchResponse) -> dict:
    data = response.model_dump()
    data["aircraft"] = [ac.model_dump() for ac in response.aircraft]
    return data


@asynccontextmanager
async def _lifespan(_server: FastMCP) -> AsyncIterator[None]:
    await startup()
    try:
        yield
    finally:
        await shutdown()


mcp = FastMCP("flightsearch", lifespan=_lifespan)


@mcp.tool()
async def search_flights(
    query: str,
    limit: int = 12,
    airborne_only: bool = True,
) -> str:
    """Search live aircraft by callsign or ICAO24 hex code over the continental US.

    Args:
        query: Callsign (e.g. UAL123) or ICAO24 hex (e.g. a1b2c3). Min 2 characters.
        limit: Maximum number of matches to return (1–50).
        airborne_only: When true, exclude aircraft on the ground.
    """
    try:
        result = await search_aircraft_in_bbox(
            resolve_bbox(None, None, None, None),
            query=query,
            limit=min(max(limit, 1), 50),
            airborne_only=airborne_only,
        )
    except OpenSkyError as exc:
        return f"OpenSky error: {exc}"

    return format_search_results(_search_payload(result))


@mcp.tool()
async def list_aircraft(
    page: int = 1,
    page_size: int = 20,
    query: str = "",
    airborne_only: bool = True,
    lamin: float | None = None,
    lomin: float | None = None,
    lamax: float | None = None,
    lomax: float | None = None,
) -> str:
    """List live aircraft in a geographic area with optional text filter.

    Defaults to the continental US bounding box. Provide all four bbox params
    to query a sub-region (values are clipped to CONUS).

    Args:
        page: Page number (1-based).
        page_size: Results per page (1–200).
        query: Optional callsign/ICAO filter (min 2 chars when provided).
        airborne_only: When true, exclude aircraft on the ground.
        lamin: Minimum latitude (south edge).
        lomin: Minimum longitude (west edge).
        lamax: Maximum latitude (north edge).
        lomax: Maximum longitude (east edge).
    """
    params = _resolve_bbox_or_message(lamin, lomin, lamax, lomax)
    if isinstance(params, str):
        return params

    try:
        result = await get_aircraft_page(
            params,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 200),
            query=query.strip() or None,
            airborne_only=airborne_only,
        )
    except OpenSkyError as exc:
        return f"OpenSky error: {exc}"

    payload = _page_payload(result)
    return format_aircraft_list(
        payload["aircraft"],
        total_count=payload["count"],
        page=payload["page"],
        total_pages=payload["total_pages"],
    )


@mcp.tool()
async def airspace_summary(
    sample_size: int = 500,
    airborne_only: bool = True,
    lamin: float | None = None,
    lomin: float | None = None,
    lamax: float | None = None,
    lomax: float | None = None,
) -> str:
    """Summarize current air traffic — counts by altitude band and origin country.

    Fetches a sample of aircraft and aggregates stats. Useful for questions like
    "how busy is the sky over Texas right now?"

    Args:
        sample_size: Number of aircraft to sample for aggregation (1–2000).
        airborne_only: When true, exclude aircraft on the ground.
        lamin: Minimum latitude (south edge).
        lomin: Minimum longitude (west edge).
        lamax: Maximum latitude (north edge).
        lomax: Maximum longitude (east edge).
    """
    params = _resolve_bbox_or_message(lamin, lomin, lamax, lomax)
    if isinstance(params, str):
        return params

    try:
        result = await get_aircraft_page(
            params,
            page=1,
            page_size=min(max(sample_size, 1), 2000),
            query=None,
            airborne_only=airborne_only,
        )
    except OpenSkyError as exc:
        return f"OpenSky error: {exc}"

    return format_airspace_summary(_page_payload(result))


@mcp.tool()
async def flight_data_status() -> str:
    """Report flight data layer status and default coverage region."""
    bbox = US_BBOX
    return (
        f"**Flight data layer ready**\n\n"
        f"- Region: {US_REGION}\n"
        f"- Data source: OpenSky Network\n"
        f"- Cache TTL: {CACHE_SECONDS}s\n\n"
        f"**Default coverage (CONUS):**\n"
        f"- Lat: {bbox['lamin']}° to {bbox['lamax']}°\n"
        f"- Lon: {bbox['lomin']}° to {bbox['lomax']}°"
    )


def main() -> None:
    load_dotenv()
    load_app_dotenv()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
