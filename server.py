from fastmcp import FastMCP

mcp = FastMCP(name="FastMCP Server")


@mcp.tool
def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9002)
