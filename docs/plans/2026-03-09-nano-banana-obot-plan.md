# Nano Banana MCP — Obot Deployment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor nano-banana-mcp into a PyPI-publishable package with STDIO transport for deployment on Obot via uvx.

**Architecture:** Move existing server code into a proper Python package under `servers/nano-banana-mcp/` with src layout. Remove auth middleware (Obot handles it). Add Obot GitOps YAML to `obot-catalog/`. Publish to PyPI.

**Tech Stack:** FastMCP, google-genai, Hatchling build system, uvx runtime on Obot

---

### Task 1: Create Package Directory Structure

**Files:**
- Create: `servers/nano-banana-mcp/src/nano_banana_mcp/__init__.py`
- Create: `servers/nano-banana-mcp/pyproject.toml`

**Step 1: Create directories**

Run:
```bash
mkdir -p servers/nano-banana-mcp/src/nano_banana_mcp
```

**Step 2: Create `__init__.py`**

Create `servers/nano-banana-mcp/src/nano_banana_mcp/__init__.py`:
```python
```
(Empty file — just marks it as a package.)

**Step 3: Create `pyproject.toml`**

Create `servers/nano-banana-mcp/pyproject.toml`:
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

**Step 4: Commit**

```bash
git add servers/nano-banana-mcp/src/nano_banana_mcp/__init__.py servers/nano-banana-mcp/pyproject.toml
git commit -m "feat: scaffold nano-banana-mcp package structure"
```

---

### Task 2: Refactor Server Code

**Files:**
- Read: `nano-banana-mcp/server.py` (original)
- Create: `servers/nano-banana-mcp/src/nano_banana_mcp/server.py` (refactored)

**Step 1: Write the refactored server**

Create `servers/nano-banana-mcp/src/nano_banana_mcp/server.py`:
```python
import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from google import genai
from google.genai import types

load_dotenv()

mcp = FastMCP(name="Nano Banana MCP")

gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


@mcp.tool
def generate_image(prompt: str) -> list[Image] | str:
    """Generate an image using Gemini. Returns the generated image."""
    response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    results = []
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            results.append(Image(data=part.inline_data.data, format="png"))

    if not results:
        return "No image was generated. Try a different prompt."

    return results


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

Changes from original:
- Removed: `BearerAuthMiddleware` class and all auth imports (`ToolError`, `get_http_headers`, `Middleware`, `MiddlewareContext`)
- Removed: `AUTH_TOKEN = os.environ["MCP_AUTH_TOKEN"]`
- Removed: `mcp.add_middleware(BearerAuthMiddleware())`
- Added: `main()` function wrapping `mcp.run(transport="stdio")`
- Changed: `__main__` block calls `main()` instead of `mcp.run(transport="http", ...)`

**Step 2: Commit**

```bash
git add servers/nano-banana-mcp/src/nano_banana_mcp/server.py
git commit -m "feat: refactor nano-banana-mcp for STDIO transport and remove auth middleware"
```

---

### Task 3: Verify Package Builds and Entry Point Works

**Step 1: Install the package in dev mode**

Run from repo root:
```bash
cd servers/nano-banana-mcp
pip install -e .
```

Expected: Successful installation, no errors.

**Step 2: Verify the console script entry point exists**

```bash
which nano-banana-mcp
```

Expected: A path to the installed script (e.g., `.venv/bin/nano-banana-mcp`).

**Step 3: Verify the package builds**

```bash
pip install build
python -m build
```

Expected: Creates `dist/nano_banana_mcp-0.1.0.tar.gz` and `dist/nano_banana_mcp-0.1.0-py3-none-any.whl` without errors.

**Step 4: Clean up build artifacts**

```bash
rm -rf dist build *.egg-info
cd ../..
```

---

### Task 4: Create Obot GitOps YAML

**Files:**
- Create: `obot-catalog/nano-banana-mcp.yaml`

**Step 1: Create the obot-catalog directory**

```bash
mkdir -p obot-catalog
```

**Step 2: Write the YAML file**

Create `obot-catalog/nano-banana-mcp.yaml`:
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

**Step 3: Commit**

```bash
git add obot-catalog/nano-banana-mcp.yaml
git commit -m "feat: add Obot GitOps catalog YAML for nano-banana-mcp"
```

---

### Task 5: Clean Up Old Server Location

**Files:**
- Delete: `nano-banana-mcp/server.py` (old location)
- Delete: `nano-banana-mcp/` directory

**Step 1: Remove the old server file**

```bash
rm nano-banana-mcp/server.py
rmdir nano-banana-mcp
```

**Step 2: Commit**

```bash
git add -A nano-banana-mcp/
git commit -m "chore: remove old nano-banana-mcp location (moved to servers/)"
```

---

### Task 6: Publish to PyPI

**Step 1: Create a PyPI account** (if you don't have one)

Go to https://pypi.org/account/register/

**Step 2: Create an API token**

Go to https://pypi.org/manage/account/token/ and create a token scoped to the `nano-banana-mcp` project (or all projects for first upload).

**Step 3: Build the package**

```bash
cd servers/nano-banana-mcp
pip install build twine
python -m build
```

**Step 4: Upload to PyPI**

```bash
twine upload dist/*
```

Enter `__token__` as username and paste your API token as password.

Expected: Package uploaded successfully to https://pypi.org/project/nano-banana-mcp/

**Step 5: Verify it installs via uvx**

```bash
uvx nano-banana-mcp --help
```

Expected: The entry point runs (it will fail without `GEMINI_API_KEY` set, but confirms the package is installable).

---

### Task 7: Register in Obot

**Step 1: Point Obot at your catalog repo**

In your Obot admin, configure a Git-based MCP registry pointing to this repo's `obot-catalog/` directory (or the repo root if Obot scans for YAML files).

**Step 2: Set the GEMINI_API_KEY credential**

In Obot admin, navigate to the Nano Banana MCP server configuration and provide your Gemini API key in the environment variable field.

**Step 3: Test via Obot**

Use the Obot chat interface or connect a client through the Obot gateway. Call the `generate_image` tool with a test prompt.

Expected: A PNG image is returned.
