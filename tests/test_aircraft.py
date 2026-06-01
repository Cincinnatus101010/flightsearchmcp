"""Tests for OpenSky row parsing and filtering."""

from flightsearch_mcp.aircraft import (
    filter_aircraft,
    paginate,
    parse_opensky_row,
    parse_opensky_rows,
    search_aircraft,
)
from tests import factory


def test_parse_opensky_row_enriches_fields() -> None:
    ac = parse_opensky_row(factory.ual818_row())
    assert ac is not None
    assert ac.icao24 == "aad012"
    assert ac.callsign == "UAL818"
    assert ac.label == "UAL818"
    assert ac.altitudeBand == "mid"
    assert ac.altitudeFt == 26182
    assert ac.speedKts == 458
    assert ac.heading == 321
    assert ac.onGround is False


def test_parse_opensky_row_uses_icao_when_callsign_missing() -> None:
    ac = parse_opensky_row(factory.ground_row())
    assert ac is not None
    assert ac.label == "ABC123"
    assert ac.altitudeBand == "ground"


def test_parse_opensky_row_rejects_short_rows() -> None:
    assert parse_opensky_row(["only"]) is None


def test_filter_aircraft_airborne_only() -> None:
    aircraft = parse_opensky_rows(factory.default_rows())
    filtered = filter_aircraft(aircraft, airborne_only=True)
    assert len(filtered) == 3
    assert all(not ac.onGround for ac in filtered)


def test_filter_aircraft_query() -> None:
    aircraft = parse_opensky_rows(factory.default_rows())
    filtered = filter_aircraft(aircraft, airborne_only=False, query="UAL")
    assert len(filtered) == 2
    assert all("UAL" in (ac.callsign or "") for ac in filtered)


def test_search_aircraft_limit() -> None:
    aircraft = parse_opensky_rows(factory.default_rows())
    matches = search_aircraft(aircraft, "UAL", limit=1)
    assert len(matches) == 1


def test_paginate() -> None:
    aircraft = parse_opensky_rows(factory.default_rows())
    page, current, total_pages = paginate(aircraft, page=1, page_size=2)
    assert len(page) == 2
    assert current == 1
    assert total_pages == 2


def test_factory_builds_custom_aircraft(make: type[factory]) -> None:
    ac = make.aircraft(callsign="SWA123", label="SWA123", icao24="swa001", altitudeBand="high")
    assert ac.callsign == "SWA123"
    assert ac.altitudeBand == "high"
