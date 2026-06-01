"""Tests for the aircraft query service layer."""

import pytest

from flightsearch_mcp.region import resolve_bbox
from flightsearch_mcp.service import get_aircraft_page, search_aircraft_in_bbox
from tests import factory


@pytest.mark.asyncio
async def test_get_aircraft_page(mock_opensky: None) -> None:
    result = await get_aircraft_page(
        resolve_bbox(None, None, None, None),
        page=1,
        page_size=2,
        query=None,
        airborne_only=True,
    )
    assert result.count == 3
    assert len(result.aircraft) == 2
    assert result.total_pages == 2
    assert result.time == factory.DEFAULT_TIME


@pytest.mark.asyncio
async def test_search_aircraft_in_bbox(mock_opensky: None) -> None:
    result = await search_aircraft_in_bbox(
        resolve_bbox(None, None, None, None),
        query="UAL",
        limit=5,
        airborne_only=True,
    )
    assert result.count == 2
    assert all("UAL" in (ac.callsign or "") for ac in result.aircraft)


@pytest.mark.asyncio
async def test_get_aircraft_page_with_query_filter(mock_opensky: None) -> None:
    result = await get_aircraft_page(
        resolve_bbox(None, None, None, None),
        page=1,
        page_size=10,
        query="AAL",
        airborne_only=True,
    )
    assert result.count == 1
    assert result.aircraft[0].callsign == "AAL2949"
