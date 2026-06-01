"""Test data factories for flightsearch-mcp."""

from __future__ import annotations

from typing import Any

from flightsearch_mcp.models import AircraftOut, AircraftPageResponse, SearchResponse
from flightsearch_mcp.region import US_BBOX, US_REGION

DEFAULT_TIME = 1717090000


def opensky_row(
    *,
    icao24: str = "aad012",
    callsign: str = "UAL818  ",
    origin_country: str = "United States",
    longitude: float = -93.9455,
    latitude: float = 29.1543,
    baro_altitude_m: float = 7980.32,
    on_ground: bool = False,
    velocity: float = 235.6,
    true_track: float = 321.0,
    vertical_rate: float = 0.0,
) -> list[object]:
    """Build a raw OpenSky state vector row."""
    return [
        icao24,
        callsign,
        origin_country,
        None,
        None,
        longitude,
        latitude,
        baro_altitude_m,
        on_ground,
        velocity,
        true_track,
        vertical_rate,
    ]


def aircraft(**overrides: Any) -> AircraftOut:
    """Build an AircraftOut model with sensible defaults."""
    defaults: dict[str, Any] = {
        "icao24": "aad012",
        "callsign": "UAL818",
        "label": "UAL818",
        "originCountry": "United States",
        "latitude": 29.1543,
        "longitude": -93.9455,
        "baroAltitude": 7980.32,
        "altitudeFt": 26182,
        "velocity": 235.6,
        "speedKts": 458,
        "trueTrack": 321.0,
        "heading": 321,
        "altitudeBand": "mid",
        "onGround": False,
        "verticalRate": 0.0,
    }
    defaults.update(overrides)
    return AircraftOut(**defaults)


def aircraft_dict(**overrides: Any) -> dict[str, Any]:
    """Build a dict suitable for formatter functions."""
    return aircraft(**overrides).model_dump()


def aircraft_page_response(**overrides: Any) -> AircraftPageResponse:
    """Build an AircraftPageResponse with defaults."""
    ac_list = overrides.pop("aircraft", [aircraft(), aircraft(callsign="AAL2949", label="AAL2949", icao24="acdfa6")])
    defaults: dict[str, Any] = {
        "time": DEFAULT_TIME,
        "aircraft": ac_list,
        "count": len(ac_list),
        "page": 1,
        "page_size": len(ac_list),
        "total_pages": 1,
        "region": US_REGION,
        "bbox": dict(US_BBOX),
        "query": None,
    }
    defaults.update(overrides)
    return AircraftPageResponse(**defaults)


def search_response(**overrides: Any) -> SearchResponse:
    """Build a SearchResponse with defaults."""
    ac_list = overrides.pop("aircraft", [aircraft()])
    defaults: dict[str, Any] = {
        "query": "UAL",
        "aircraft": ac_list,
        "count": len(ac_list),
        "region": US_REGION,
        "bbox": dict(US_BBOX),
    }
    defaults.update(overrides)
    return SearchResponse(**defaults)


def ual818_row() -> list[object]:
    return opensky_row()


def aal2949_row() -> list[object]:
    return opensky_row(
        icao24="acdfa6",
        callsign="AAL2949 ",
        longitude=-110.9221,
        latitude=37.0579,
        baro_altitude_m=11277.6,
        velocity=258.9,
        true_track=71.0,
    )


def ground_row() -> list[object]:
    return opensky_row(
        icao24="abc123",
        callsign="        ",
        origin_country="Canada",
        longitude=-100.0,
        latitude=35.0,
        baro_altitude_m=0.0,
        on_ground=True,
        velocity=0.0,
        true_track=0.0,
    )


def ual327_row() -> list[object]:
    return opensky_row(
        icao24="a5d319",
        callsign="UAL327  ",
        longitude=-82.924,
        latitude=41.8866,
        baro_altitude_m=10668.0,
        velocity=261.5,
        true_track=94.0,
    )


def default_rows() -> list[list[object]]:
    """Standard OpenSky payload used across tests."""
    return [ual818_row(), aal2949_row(), ground_row(), ual327_row()]


async def mock_opensky_fetch(
    _params: dict[str, float],
    *,
    rows: list[list[object]] | None = None,
    upstream_time: int | None = DEFAULT_TIME,
) -> tuple[list[list[object]], int | None]:
    """Async fetch stub matching the service layer signature."""
    return rows if rows is not None else default_rows(), upstream_time
