"""In-memory cache for processed OpenSky responses."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from .models import AircraftOut


@dataclass
class CacheEntry:
    expires_at: float
    time: int | None
    aircraft: list[AircraftOut]


class AircraftCache:
    def __init__(self) -> None:
        self._entries: dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> CacheEntry | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.expires_at <= time.monotonic():
                self._entries.pop(key, None)
                return None
            return entry

    def set(
        self,
        key: str,
        *,
        upstream_time: int | None,
        aircraft: list[AircraftOut],
        ttl_seconds: int,
    ) -> None:
        if ttl_seconds <= 0:
            return
        with self._lock:
            self._entries[key] = CacheEntry(
                expires_at=time.monotonic() + ttl_seconds,
                time=upstream_time,
                aircraft=aircraft,
            )


aircraft_cache = AircraftCache()
