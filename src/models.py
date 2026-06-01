"""Public response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

AltitudeBand = Literal["low", "mid", "high", "ground", "unknown"]


class AircraftOut(BaseModel):
    icao24: str
    callsign: str | None = None
    label: str
    originCountry: str
    latitude: float
    longitude: float
    baroAltitude: float | None = None
    altitudeFt: int | None = None
    velocity: float | None = None
    speedKts: int | None = None
    trueTrack: float | None = None
    heading: int | None = None
    altitudeBand: AltitudeBand = "unknown"
    onGround: bool = False
    verticalRate: float | None = None


class AircraftPageResponse(BaseModel):
    time: int | None
    aircraft: list[AircraftOut]
    count: int
    page: int
    page_size: int
    total_pages: int
    region: str
    bbox: dict[str, float]
    query: str | None = None
    source: str = "opensky-network.org"
    authenticated: bool = False


class SearchResponse(BaseModel):
    query: str
    aircraft: list[AircraftOut]
    count: int
    region: str
    bbox: dict[str, float]
    source: str = "opensky-network.org"
