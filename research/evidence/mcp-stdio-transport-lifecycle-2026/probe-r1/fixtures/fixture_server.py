#!/usr/bin/env python3
"""Minimal MCP stdio server used as a controllable fixture by probe_stdio_lifecycle.py.

Behaviour is driven by two environment variables:
  FIXTURE_NAME    server name reported in initialize (default "fixture")
  FIXTURE_CATALOG path to a JSON file holding a list of tool names. The file is
                  re-read on every tools/list request, so a caller can change the
                  server's advertised catalog between two registrations.

The tool list is deliberately dynamic: scenario L4 needs the same server process
to advertise a different catalog on a second registration.
"""
import json
import os
import sys

import anyio
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp import types

NAME = os.environ.get("FIXTURE_NAME", "fixture")
CATALOG = os.environ.get("FIXTURE_CATALOG", "")


def catalog():
    if CATALOG and os.path.exists(CATALOG):
        with open(CATALOG) as fh:
            names = json.load(fh)
    else:
        names = ["echo"]
    return [types.Tool(name=n, description=f"fixture tool {n}", inputSchema={"type": "object"}) for n in names]


async def on_list_tools(ctx, params):
    return types.ListToolsResult(tools=catalog())


async def on_call_tool(ctx, params):
    return types.CallToolResult(content=[types.TextContent(type="text", text="ok")])


async def main():
    server = Server(NAME, version="0.0.1", on_list_tools=on_list_tools, on_call_tool=on_call_tool)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    try:
        anyio.run(main)
    except BaseException as exc:  # noqa: BLE001 - fixture must expose what ended it
        print(f"FIXTURE_EXIT {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise
