"""Startup and shutdown for the flight data layer."""

from __future__ import annotations

from .executor import shutdown_parse_executor
from .opensky_client import shutdown_opensky_client, startup_opensky_client


async def startup() -> None:
    await startup_opensky_client()


async def shutdown() -> None:
    await shutdown_opensky_client()
    shutdown_parse_executor()
