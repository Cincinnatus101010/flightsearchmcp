"""Tests for MCP tool handlers."""

import pytest

from flightsearch_mcp import opensky_client, service as service_module
from flightsearch_mcp.server import mcp
from tests.helpers import call_tool


def test_tools_are_registered() -> None:
    names = sorted(tool.name for tool in mcp._tool_manager.list_tools())
    assert names == [
        "airspace_summary",
        "flight_data_status",
        "list_aircraft",
        "search_flights",
    ]


@pytest.mark.asyncio
async def test_flight_data_status(mock_mcp_session: None) -> None:
    result = await call_tool("flight_data_status")
    assert "Flight data layer ready" in result
    assert "us-conus" in result


@pytest.mark.asyncio
async def test_list_aircraft_rejects_partial_bbox(mock_mcp_session: None) -> None:
    result = await call_tool("list_aircraft", {"lamin": 30.0})
    assert "Provide all bounding box" in result


@pytest.mark.asyncio
async def test_list_aircraft_returns_data(mock_mcp_session: None) -> None:
    result = await call_tool("list_aircraft", {"page_size": 2})
    assert "UAL818" in result
    assert "Showing 2 of 3 aircraft" in result


@pytest.mark.asyncio
async def test_search_flights(mock_mcp_session: None) -> None:
    result = await call_tool("search_flights", {"query": "UAL", "limit": 2})
    assert "Search results for **UAL**" in result
    assert "UAL818" in result
    assert "UAL327" in result


@pytest.mark.asyncio
async def test_airspace_summary(mock_mcp_session: None) -> None:
    result = await call_tool("airspace_summary", {"sample_size": 10})
    assert "Airspace summary" in result
    assert "Total airborne aircraft:" in result


@pytest.mark.asyncio
async def test_opensky_error_surfaces_to_tool(
    mock_mcp_session: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fail(_params: dict[str, float]) -> tuple[list[list[object]], int | None]:
        raise opensky_client.OpenSkyError("Could not reach OpenSky Network.")

    monkeypatch.setattr(service_module, "fetch_opensky_states", _fail)

    result = await call_tool("list_aircraft", {"page_size": 1})
    assert "OpenSky error" in result
