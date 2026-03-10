# Nano Banana MCP — Obot Deployment Design

## Summary

Refactor nano-banana-mcp from a standalone FastMCP HTTP server into a PyPI-publishable package that runs via `uvx` on the Obot MCP platform. Authentication moves from custom middleware to Obot's gateway. The Gemini API key is admin-managed through Obot's credential system.

## Approach

**Minimal refactor (Approach A):** Keep FastMCP framework, switch transport to STDIO, remove auth middleware, add Python packaging.

## Repo Structure

```
fast-mcp/
├── servers/
│   └── nano-banana-mcp/
│       ├── pyproject.toml
│       └── src/
│           └── nano_banana_mcp/
│               ├── __init__.py
│               └── server.py
├── obot-catalog/
│   └── nano-banana-mcp.yaml
├── server.py                   # Existing demo server (unchanged)
└── .mcp.json
```

Future MCP servers follow the same pattern: a new directory under `servers/` and a new YAML in `obot-catalog/`.

## Server Code Changes

Starting from `nano-banana-mcp/server.py`:

- **Remove:** `BearerAuthMiddleware`, all auth-related imports (`get_http_headers`, `MiddlewareContext`, `Middleware`, `ToolError`), `AUTH_TOKEN` env var lookup
- **Keep:** `generate_image` tool (unchanged logic, type hints, docstring), `gemini_client` initialization from `GEMINI_API_KEY`
- **Change:** Transport from `http` to `stdio`, add `main()` entry point function

## Package Configuration

```toml
[project]
name = "nano-banana-mcp"
version = "0.1.0"
description = "MCP server for image generation using Google Gemini"
requires-python = ">=3.13"
dependencies = [
    "fastmcp",
    "google-genai",
    "python-dotenv",
]

[project.scripts]
nano-banana-mcp = "nano_banana_mcp.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Obot GitOps YAML

```yaml
name: Nano Banana MCP
description: |
  Generate images using Google Gemini 3.1 Flash. Provide a text prompt
  and receive a PNG image.

toolPreview:
  - name: generate_image
    description: Generate an image using Gemini. Returns the generated image.
    params:
      prompt: Text description of the image to generate

metadata:
  categories: AI Image Generation

runtime: uvx
uvxConfig:
  package: 'nano-banana-mcp@latest'

env:
  - key: GEMINI_API_KEY
    name: Gemini API Key
    required: true
    sensitive: true
    description: Google Gemini API key for image generation
```

## Key Decisions

- **Auth:** Removed from server code; Obot gateway handles user-facing authentication
- **GEMINI_API_KEY:** Single admin-managed secret, injected by Obot as env var
- **Package name:** `nano-banana-mcp` on public PyPI
- **Build backend:** Hatchling
- **Obot catalog:** Lives in same repo under `obot-catalog/`
