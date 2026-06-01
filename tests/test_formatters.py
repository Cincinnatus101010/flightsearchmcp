"""Tests for MCP response formatters."""

from flightsearch_mcp.formatters import (
    format_aircraft_list,
    format_aircraft_row,
    format_airspace_summary,
    format_search_results,
)
from tests import factory


def test_format_aircraft_row() -> None:
    text = format_aircraft_row(factory.aircraft_dict())
    assert "UAL818" in text
    assert "458 kts" in text


def test_format_aircraft_list_empty() -> None:
    assert format_aircraft_list([]) == "No aircraft found."


def test_format_search_results() -> None:
    payload = factory.search_response().model_dump()
    payload["aircraft"] = [ac.model_dump() for ac in factory.search_response().aircraft]
    text = format_search_results(payload)
    assert "Search results for **UAL**" in text
    assert "UAL818" in text


def test_format_airspace_summary() -> None:
    page = factory.aircraft_page_response(
        count=100,
        aircraft=[
            factory.aircraft(altitudeBand="high"),
            factory.aircraft(altitudeBand="mid", callsign="AAL2949", label="AAL2949", icao24="acdfa6"),
            factory.aircraft(altitudeBand="high", originCountry="Canada"),
        ],
    )
    text = format_airspace_summary(page.model_dump())
    assert "Airspace summary" in text
    assert "high: 2" in text
    assert "United States: 2" in text
