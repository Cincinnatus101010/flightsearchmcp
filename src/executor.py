"""Shared thread pool for CPU-bound aircraft processing."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from .config import PARSE_CHUNK_SIZE, PARSE_WORKERS

_executor: ThreadPoolExecutor | None = None


def get_parse_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(
            max_workers=PARSE_WORKERS,
            thread_name_prefix="aircraft-parse",
        )
    return _executor


def shutdown_parse_executor() -> None:
    global _executor
    if _executor is not None:
        _executor.shutdown(wait=False, cancel_futures=True)
        _executor = None


def parse_chunk_size() -> int:
    return PARSE_CHUNK_SIZE
