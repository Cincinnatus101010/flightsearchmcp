"""Runtime configuration loaded from environment."""

from __future__ import annotations

import os
from pathlib import Path

OPENSKY_BASE = "https://opensky-network.org/api"

CACHE_SECONDS = max(0, int(os.getenv("STATES_CACHE_SECONDS", "10")))

_cpu_count = os.cpu_count() or 4
PARSE_WORKERS = max(1, int(os.getenv("PARSE_WORKERS", str(min(32, _cpu_count + 4)))))
PARSE_CHUNK_SIZE = max(100, int(os.getenv("PARSE_CHUNK_SIZE", "500")))


def load_dotenv() -> None:
    path = Path(".env")
    if not path.is_file():
        return

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
