# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Minimal MCP (Model Context Protocol) server built with Python's FastMCP framework. Exposes tools that can be called by Claude and other LLM clients over HTTP.

## Running the Server

```bash
source .venv/bin/activate
python server.py
```

Server starts on `0.0.0.0:9002`, MCP endpoint at `http://localhost:9002/mcp`.

## Architecture

- **server.py** — Single-file server. Uses `FastMCP` class and `@mcp.tool` decorators to define tools. Runs via uvicorn with HTTP transport.
- **.mcp.json** — Client configuration file that registers this server for Claude Code integration.

## Adding New Tools

Define tools with the `@mcp.tool` decorator on the `mcp` instance. FastMCP uses type hints and docstrings for schema generation:

```python
@mcp.tool
def my_tool(param: str) -> str:
    """Description used by LLM clients."""
    return result
```

## Dependencies

- Python 3.13+ with virtual environment in `.venv/`
- `fastmcp` (v3.x) — installed via `pip install fastmcp`

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

Then connect to `http://localhost:9002/mcp` using Streamable HTTP transport.
