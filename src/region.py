"""Geographic region constraints."""

from __future__ import annotations

US_BBOX: dict[str, float] = {
    "lamin": 24.5,
    "lomin": -125.0,
    "lamax": 49.5,
    "lomax": -66.5,
}
US_REGION = "us-conus"


def cache_key(params: dict[str, float]) -> str:
    if not params:
        return US_REGION
    return "|".join(f"{key}={params[key]}" for key in sorted(params))


def resolve_bbox(
    lamin: float | None,
    lomin: float | None,
    lamax: float | None,
    lomax: float | None,
) -> dict[str, float] | None:
    """Intersect optional viewport params with the US bounding box."""
    if not any(value is not None for value in (lamin, lomin, lamax, lomax)):
        return dict(US_BBOX)

    if not all(value is not None for value in (lamin, lomin, lamax, lomax)):
        raise ValueError("Provide all bounding box params: lamin, lomin, lamax, lomax.")

    resolved = {
        "lamin": max(lamin, US_BBOX["lamin"]),  # type: ignore[type-var]
        "lomin": max(lomin, US_BBOX["lomin"]),  # type: ignore[type-var]
        "lamax": min(lamax, US_BBOX["lamax"]),  # type: ignore[type-var]
        "lomax": min(lomax, US_BBOX["lomax"]),  # type: ignore[type-var]
    }

    if resolved["lamin"] >= resolved["lamax"] or resolved["lomin"] >= resolved["lomax"]:
        return None

    return resolved
