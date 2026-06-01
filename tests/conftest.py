"""Shared pytest fixtures and helpers."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable

import pytest
import pytest_asyncio

from flightsearch_mcp import cache as cache_module
from flightsearch_mcp import opensky_client
from flightsearch_mcp import service as service_module
from flightsearch_mcp.lifecycle import startup
from tests import factory


@pytest.fixture
def make() -> type[factory]:
    """Access test data factories."""
    return factory


@pytest.fixture(autouse=True)
def reset_state() -> None:
    cache_module.aircraft_cache._entries.clear()
    service_module._inflight.clear()
    opensky_client._client = None


@pytest.fixture
def mock_opensky(monkeypatch: pytest.MonkeyPatch) -> Callable[..., None]:
    def _apply(*, rows: list[list[object]] | None = None) -> None:
        async def _fetch(params: dict[str, float]) -> tuple[list[list[object]], int | None]:
            return await factory.mock_opensky_fetch(params, rows=rows)

        monkeypatch.setattr(service_module, "fetch_opensky_states", _fetch)

    _apply()
    return _apply


@pytest_asyncio.fixture
async def mcp_session() -> AsyncIterator[None]:
    await startup()
    try:
        yield
    finally:
        opensky_client._client = None


@pytest_asyncio.fixture
async def mock_mcp_session(mock_opensky: Callable[..., None]) -> AsyncIterator[None]:
    await startup()
    try:
        yield
    finally:
        opensky_client._client = None
