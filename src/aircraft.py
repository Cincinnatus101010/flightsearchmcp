"""Parse and enrich OpenSky state vectors."""

from __future__ import annotations

import math

from .models import AircraftOut, AltitudeBand

METERS_TO_FEET = 3.28084
METERS_PER_SECOND_TO_KNOTS = 1.94384


def meters_to_feet(meters: float | None) -> int | None:
    if meters is None:
        return None
    return round(meters * METERS_TO_FEET)


def meters_per_second_to_knots(speed: float | None) -> int | None:
    if speed is None:
        return None
    return round(speed * METERS_PER_SECOND_TO_KNOTS)


def aircraft_label(callsign: str | None, icao24: str) -> str:
    if callsign:
        return callsign
    return icao24.upper()


def altitude_band(
    altitude_m: float | None,
    on_ground: bool,
) -> AltitudeBand:
    if on_ground:
        return "ground"
    if altitude_m is None:
        return "unknown"
    if altitude_m < 3000:
        return "low"
    if altitude_m < 9000:
        return "mid"
    return "high"


def parse_opensky_row(row: list[object]) -> AircraftOut | None:
    if len(row) < 12:
        return None

    latitude = row[6] if isinstance(row[6], (int, float)) else None
    longitude = row[5] if isinstance(row[5], (int, float)) else None
    if latitude is None or longitude is None:
        return None

    callsign_raw = row[1]
    callsign = str(callsign_raw).strip() if callsign_raw else None
    if callsign == "":
        callsign = None

    icao24 = str(row[0])
    on_ground = bool(row[8])
    baro_altitude = row[7] if isinstance(row[7], (int, float)) else None
    velocity = row[9] if isinstance(row[9], (int, float)) else None
    true_track = row[10] if isinstance(row[10], (int, float)) else None
    vertical_rate = row[11] if isinstance(row[11], (int, float)) else None

    return AircraftOut(
        icao24=icao24,
        callsign=callsign,
        label=aircraft_label(callsign, icao24),
        originCountry=str(row[2] or ""),
        latitude=float(latitude),
        longitude=float(longitude),
        baroAltitude=baro_altitude,
        altitudeFt=meters_to_feet(baro_altitude),
        velocity=velocity,
        speedKts=meters_per_second_to_knots(velocity),
        trueTrack=true_track,
        heading=round(true_track) if true_track is not None else None,
        altitudeBand=altitude_band(baro_altitude, on_ground),
        onGround=on_ground,
        verticalRate=vertical_rate,
    )


def parse_opensky_rows(rows: list[list[object]]) -> list[AircraftOut]:
    aircraft: list[AircraftOut] = []
    for row in rows:
        parsed = parse_opensky_row(row)
        if parsed is not None:
            aircraft.append(parsed)
    return aircraft


def _parse_opensky_chunk(rows: list[list[object]]) -> list[AircraftOut]:
    return parse_opensky_rows(rows)


def parse_opensky_rows_parallel(
    rows: list[list[object]],
    *,
    chunk_size: int = 500,
) -> list[AircraftOut]:
    """Parse large OpenSky payloads using a thread pool."""
    if len(rows) <= chunk_size:
        return parse_opensky_rows(rows)

    from .executor import get_parse_executor

    chunks = [rows[index : index + chunk_size] for index in range(0, len(rows), chunk_size)]
    executor = get_parse_executor()
    parsed_chunks = executor.map(_parse_opensky_chunk, chunks)
    return [aircraft for chunk in parsed_chunks for aircraft in chunk]


def is_plottable(aircraft: AircraftOut) -> bool:
    return not aircraft.onGround


def matches_query(aircraft: AircraftOut, query: str) -> bool:
    normalized = query.strip().lower()
    if len(normalized) < 2:
        return True

    callsign = aircraft.callsign.lower() if aircraft.callsign else ""
    return (
        normalized in aircraft.icao24.lower()
        or normalized in callsign
        or normalized in aircraft.originCountry.lower()
    )


def filter_aircraft(
    aircraft: list[AircraftOut],
    *,
    airborne_only: bool = True,
    query: str | None = None,
) -> list[AircraftOut]:
    filtered: list[AircraftOut] = []
    for item in aircraft:
        if airborne_only and not is_plottable(item):
            continue
        if query and not matches_query(item, query):
            continue
        filtered.append(item)
    return filtered


def search_aircraft(
    aircraft: list[AircraftOut],
    query: str,
    *,
    limit: int = 12,
) -> list[AircraftOut]:
    normalized = query.strip().lower()
    if len(normalized) < 2:
        return []

    matches: list[AircraftOut] = []
    for item in aircraft:
        if matches_query(item, normalized):
            matches.append(item)
            if len(matches) >= limit:
                break
    return matches


def paginate(
    aircraft: list[AircraftOut],
    page: int,
    page_size: int,
) -> tuple[list[AircraftOut], int, int]:
    total = len(aircraft)
    total_pages = max(1, math.ceil(total / page_size))
    current_page = min(page, total_pages)
    start = (current_page - 1) * page_size
    return aircraft[start : start + page_size], current_page, total_pages
