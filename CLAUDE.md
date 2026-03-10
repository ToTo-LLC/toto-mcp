# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Monorepo of MCP servers published to PyPI and deployed to an Obot instance at `https://obot.tomorrowtoday.com/`. Each server is a standalone Python package under `servers/` with an Obot catalog YAML at the repo root.

## Repo Structure

```
toto-mcp/
├── server.py                    # Root demo server (HTTP on :9002, not published)
├── .mcp.json                    # Claude Code client config (gitignored)
├── .ignoreobotcatalogs          # Tells Obot to skip non-catalog dirs
├── nano-banana-mcp.yaml         # Obot catalog YAML (at repo root!)
├── servers/
│   └── nano-banana-mcp/         # Published MCP server
│       ├── pyproject.toml
│       └── src/nano_banana_mcp/
│           ├── __init__.py
│           └── server.py
├── docs/plans/
└── .github/workflows/publish.yml
```

## Adding a New MCP Server

### 1. Create the server package

```
servers/<name>/
├── pyproject.toml
└── src/<package_name>/
    ├── __init__.py
    └── server.py
```

### 2. Server code requirements

- Use `FastMCP` with STDIO transport: `mcp.run(transport="stdio")`
- **DO NOT** require environment variables at startup — Obot runs a health check before env vars are available. Defer any credential checks to tool call time, or accept credentials as tool parameters.
- **DO NOT** add auth middleware — Obot gateway handles authentication

```python
from fastmcp import FastMCP

mcp = FastMCP(name="My Server")

@mcp.tool
def my_tool(param: str, api_key: str) -> str:
    """Tool description. API keys should be tool parameters, not env vars."""
    return result

def main():
    mcp.run(transport="stdio")
```

### 3. pyproject.toml

- Package name: `toto-<name>` (PyPI namespace prefix)
- **Must** include `[tool.hatch.build.targets.wheel] packages = [...]` if the source directory name doesn't match the PyPI package name
- Console script entry point is required

```toml
[project]
name = "toto-<name>"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["fastmcp>=2.0,<4.0"]

[project.scripts]
<name> = "<package_name>.server:main"

[tool.hatch.build.targets.wheel]
packages = ["src/<package_name>"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 4. Obot catalog YAML (at repo root, NOT in a subdirectory)

Obot reads YAML files from the repo root. The `.ignoreobotcatalogs` file excludes `.github/`, `docs/`, and `servers/`.

**Critical fields:**
- `runtime: uvx` — the only supported runtime for PyPI packages
- `uvxConfig.command` — **MUST match** the console script name from pyproject.toml, or Obot won't know which entry point to run

```yaml
name: My Server
description: |
  What this server does.

toolPreview:
  - name: my_tool
    description: What the tool does.
    params:
      param: Description of param

metadata:
  categories: Category Name

runtime: uvx
uvxConfig:
  package: 'toto-<name>@latest'
  command: <name>
```

### 5. Publish

Tag with `<name>-v<version>` to trigger the GitHub Actions publish workflow:

```bash
git tag <name>-v0.1.0
git push origin <name>-v0.1.0
```

### 6. Register in Obot

Add Git Source URL `https://github.com/ToTo-LLC/toto-mcp` in Obot admin. Each new package needs a separate PyPI Trusted Publisher entry pointing to `publish.yml` workflow.

## Publishing (PyPI)

- Trusted Publisher auth via GitHub Actions (no API tokens needed)
- Workflow: `.github/workflows/publish.yml` — supports all servers via tag pattern `<name>-v*`
- Each new package must be registered as a Trusted Publisher on PyPI:
  - Owner: `ToTo-LLC`, Repo: `toto-mcp`, Workflow: `publish.yml`, Environment: `pypi`
- `dist/` is gitignored — never commit build artifacts

## Common Pitfalls

1. **Obot catalog YAMLs must be at repo root** — not in a subdirectory
2. **`uvxConfig.command` is required** — without it Obot can't run the server
3. **No env vars at startup** — server must start healthy without any env vars set
4. **Hatchling package discovery** — if PyPI name differs from source dir, add explicit `packages` in `[tool.hatch.build.targets.wheel]`
5. **Obot caches servers** — delete and re-add the catalog when debugging deployment issues

## Running the Demo Server

```bash
source .venv/bin/activate
python server.py
```

Starts on `0.0.0.0:9002`, MCP endpoint at `http://localhost:9002/mcp`.

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

Connect to `http://localhost:9002/mcp` using Streamable HTTP transport.
