"""Business logic for aircraft queries."""

from __future__ import annotations

import asyncio

from .aircraft import (
    filter_aircraft,
    paginate,
    parse_opensky_rows_parallel,
    search_aircraft,
)
from .cache import aircraft_cache
from .config import CACHE_SECONDS
from .executor import parse_chunk_size
from .models import AircraftOut, AircraftPageResponse, SearchResponse
from .opensky_client import fetch_opensky_states
from .region import US_BBOX, US_REGION, cache_key

_inflight_lock = asyncio.Lock()
_inflight: dict[str, asyncio.Task[tuple[list[AircraftOut], int | None]]] = {}


def empty_page(page_size: int) -> AircraftPageResponse:
    return AircraftPageResponse(
        time=None,
        aircraft=[],
        count=0,
        page=1,
        page_size=page_size,
        total_pages=1,
        region=US_REGION,
        bbox=US_BBOX,
        query=None,
    )


async def _fetch_and_parse(params: dict[str, float]) -> tuple[list[AircraftOut], int | None]:
    rows, upstream_time = await fetch_opensky_states(params)
    aircraft = await asyncio.to_thread(
        parse_opensky_rows_parallel,
        rows,
        chunk_size=parse_chunk_size(),
    )

    aircraft_cache.set(
        cache_key(params),
        upstream_time=upstream_time,
        aircraft=aircraft,
        ttl_seconds=CACHE_SECONDS,
    )
    return aircraft, upstream_time


async def load_aircraft_for_bbox(params: dict[str, float]) -> tuple[list[AircraftOut], int | None]:
    key = cache_key(params)
    cached = aircraft_cache.get(key)
    if cached is not None:
        return cached.aircraft, cached.time

    task: asyncio.Task[tuple[list[AircraftOut], int | None]] | None = None
    created_task = False

    async with _inflight_lock:
        cached = aircraft_cache.get(key)
        if cached is not None:
            return cached.aircraft, cached.time

        existing = _inflight.get(key)
        if existing is not None:
            task = existing
        else:
            task = asyncio.create_task(_fetch_and_parse(params))
            _inflight[key] = task
            created_task = True

    assert task is not None

    try:
        return await task
    finally:
        if created_task:
            async with _inflight_lock:
                if _inflight.get(key) is task:
                    _inflight.pop(key, None)


async def get_aircraft_page(
    params: dict[str, float] | None,
    *,
    page: int,
    page_size: int,
    query: str | None,
    airborne_only: bool,
) -> AircraftPageResponse:
    if params is None:
        return empty_page(page_size)

    aircraft, upstream_time = await load_aircraft_for_bbox(params)
    filtered = await asyncio.to_thread(
        filter_aircraft,
        aircraft,
        airborne_only=airborne_only,
        query=query,
    )
    page_rows, current_page, total_pages = paginate(filtered, page, page_size)

    return AircraftPageResponse(
        time=upstream_time,
        aircraft=page_rows,
        count=len(filtered),
        page=current_page,
        page_size=page_size,
        total_pages=total_pages,
        region=US_REGION,
        bbox=params,
        query=query.strip() if query and query.strip() else None,
    )


async def search_aircraft_in_bbox(
    params: dict[str, float] | None,
    *,
    query: str,
    limit: int,
    airborne_only: bool,
) -> SearchResponse:
    bbox = params or dict(US_BBOX)
    if params is None:
        return SearchResponse(
            query=query.strip(),
            aircraft=[],
            count=0,
            region=US_REGION,
            bbox=US_BBOX,
        )

    aircraft, _upstream_time = await load_aircraft_for_bbox(params)
    filtered = await asyncio.to_thread(
        filter_aircraft,
        aircraft,
        airborne_only=airborne_only,
    )
    matches = await asyncio.to_thread(search_aircraft, filtered, query, limit=limit)

    return SearchResponse(
        query=query.strip(),
        aircraft=matches,
        count=len(matches),
        region=US_REGION,
        bbox=bbox,
    )
