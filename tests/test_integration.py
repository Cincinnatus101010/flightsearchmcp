"""Optional live tests against OpenSky Network."""

import httpx
import pytest

from tests.helpers import call_tool


def _opensky_reachable() -> bool:
    try:
        response = httpx.get(
            "https://opensky-network.org/api/states/all",
            params={"lamin": 24.5, "lomin": -125.0, "lamax": 49.5, "lomax": -66.5},
            timeout=10.0,
        )
        return response.status_code == 200
    except httpx.HTTPError:
        return False


pytestmark = pytest.mark.skipif(not _opensky_reachable(), reason="OpenSky Network unreachable")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_list_aircraft(mcp_session: None) -> None:
    result = await call_tool("list_aircraft", {"page_size": 3})
    assert "Showing" in result
    assert "OpenSky error" not in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_search_flights(mcp_session: None) -> None:
    result = await call_tool("search_flights", {"query": "UAL", "limit": 3})
    assert "Search results" in result or "No aircraft matched" in result
    assert "OpenSky error" not in result
