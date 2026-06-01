"""Test helpers."""

from __future__ import annotations

from typing import Any

from flightsearch_mcp.server import mcp


async def call_tool(name: str, args: dict[str, Any] | None = None) -> str:
    args = args or {}
    tools = {tool.name: tool.fn for tool in mcp._tool_manager.list_tools()}
    return await tools[name](**args)
