"""Human-readable formatting for MCP tool responses."""

from __future__ import annotations

from collections import Counter
from typing import Any


def format_aircraft_row(ac: dict[str, Any]) -> str:
    label = ac.get("label") or ac.get("icao24", "?")
    lat = ac.get("latitude")
    lon = ac.get("longitude")
    alt_ft = ac.get("altitudeFt")
    speed = ac.get("speedKts")
    heading = ac.get("heading")
    country = ac.get("originCountry", "")
    band = ac.get("altitudeBand", "unknown")

    position = f"{lat:.4f}, {lon:.4f}" if lat is not None and lon is not None else "unknown"
    alt = f"{alt_ft:,} ft" if alt_ft is not None else "n/a"
    spd = f"{speed} kts" if speed is not None else "n/a"
    hdg = f"{heading}°" if heading is not None else "n/a"

    return (
        f"**{label}** ({ac.get('icao24', '')}) — {country}\n"
        f"  Position: {position} | Alt: {alt} ({band}) | Speed: {spd} | Hdg: {hdg}"
    )


def format_aircraft_list(
    aircraft: list[dict[str, Any]],
    *,
    total_count: int | None = None,
    page: int | None = None,
    total_pages: int | None = None,
) -> str:
    if not aircraft:
        return "No aircraft found."

    lines = [format_aircraft_row(ac) for ac in aircraft]

    header_parts: list[str] = [f"Showing {len(aircraft)} aircraft"]
    if total_count is not None:
        header_parts[0] = f"Showing {len(aircraft)} of {total_count} aircraft"
    if page is not None and total_pages is not None:
        header_parts.append(f"page {page}/{total_pages}")

    return "\n\n".join([", ".join(header_parts)] + lines)


def format_search_results(data: dict[str, Any]) -> str:
    query = data.get("query", "")
    aircraft = data.get("aircraft", [])
    if not aircraft:
        return f"No aircraft matched '{query}'."

    lines = [f"Search results for **{query}** ({len(aircraft)} matches):\n"]
    lines.extend(format_aircraft_row(ac) for ac in aircraft)
    return "\n\n".join(lines)


def format_airspace_summary(data: dict[str, Any]) -> str:
    aircraft = data.get("aircraft", [])
    total = data.get("count", len(aircraft))
    bbox = data.get("bbox", {})
    region = data.get("region", "unknown")
    sampled = len(aircraft)

    bands = Counter(ac.get("altitudeBand", "unknown") for ac in aircraft)
    countries = Counter(ac.get("originCountry", "Unknown") for ac in aircraft)

    lines = [
        f"## Airspace summary ({region})",
        "",
        f"**Total airborne aircraft:** {total:,}",
    ]
    if sampled < total:
        lines.append(f"*Stats below based on sample of {sampled:,} aircraft.*")
    lines.append("")

    if bbox:
        lines.append(
            f"**Bounding box:** "
            f"{bbox.get('lamin')}°N–{bbox.get('lamax')}°N, "
            f"{bbox.get('lomin')}°W–{bbox.get('lomax')}°W"
        )
        lines.append("")

    lines.append("### Altitude bands")
    for band in ("high", "mid", "low", "ground", "unknown"):
        count = bands.get(band, 0)
        if count:
            lines.append(f"- {band}: {count:,}")

    lines.append("")
    lines.append("### Top origin countries")
    for country, count in countries.most_common(8):
        lines.append(f"- {country}: {count:,}")

    return "\n".join(lines)
