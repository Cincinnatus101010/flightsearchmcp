# Flight Search MCP

An [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes live aircraft search and airspace analytics tools. Fetches data directly from the [OpenSky Network](https://opensky-network.org/), parses state vectors, caches results, and serves map-ready aircraft data — no separate backend required.

Give any MCP-compatible client (Claude Desktop, custom agents, etc.) the ability to search flights by callsign, browse aircraft in a region, and summarize current air traffic over the continental US.

## Architecture

```text
MCP client  →  flightsearch-mcp (stdio)
                     │
         parse · filter · cache · format
                     │
              OpenSky Network
```

Everything runs in one process: the MCP server owns OpenSky fetching, parallel parsing, in-memory caching, and LLM-friendly response formatting.

## Tools

| Tool | Description |
|------|-------------|
| `search_flights` | Find aircraft by callsign or ICAO24 hex |
| `list_aircraft` | Paginated aircraft list with optional bbox + text filter |
| `airspace_summary` | Aggregate stats — altitude bands, top origin countries |
| `flight_data_status` | Region metadata and cache configuration |

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Quick start

```bash
git clone https://github.com/Cincinnatus101010/flightsearchmcp
cd flightsearchmcp
uv sync
cp .env.example .env   # optional — tune cache TTL
uv run flightsearch-mcp
```

## Tests

```bash
uv sync --group dev
uv run pytest
```

Live OpenSky tests run automatically when the network is reachable; they are skipped on VPNs or offline environments.

```bash
uv run pytest -m integration   # live tests only
```

The server communicates over **stdio** — it waits for MCP clients to connect. No other services need to be running.

## Client configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flightsearch": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/flightsearchmcp",
        "run",
        "flightsearch-mcp"
      ]
    }
  }
}
```

### MCP Inspector (development)

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/flightsearchmcp run flightsearch-mcp
```

## Example prompts

Once connected to an MCP client:

- *"Search for flight UAL123"*
- *"How many aircraft are airborne over the US right now?"*
- *"List 10 aircraft near Denver"* (with bbox: ~39°N, -105°W)
- *"Summarize air traffic in Texas"* (bbox: 25.8–36.5°N, -106.6–-93.5°W)

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `STATES_CACHE_SECONDS` | `10` | Cache OpenSky responses for N seconds |
| `PARSE_WORKERS` | CPU-based | Thread pool size for parallel parsing |
| `PARSE_CHUNK_SIZE` | `500` | Rows per parse chunk |

## Project layout

```text
src/
  server.py           # FastMCP tools + entry point
  service.py          # Query orchestration
  aircraft.py         # Parse OpenSky state vectors
  opensky_client.py   # OpenSky HTTP client
  cache.py            # In-memory TTL cache
  formatters.py       # Markdown formatters for tool output
  models.py           # Pydantic models
  config.py           # Environment configuration
  region.py           # CONUS bounding box
  lifecycle.py        # Startup / shutdown
  executor.py         # Thread pool for parsing
```

## Related projects

- **[portfolio](https://github.com/Cincinnatus101010/portfolio)** — Next.js flight radar demo (companion UI project)

## License

MIT
