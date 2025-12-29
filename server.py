from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="MyMCPServer",
    port=8050,
)

@mcp.tool(name="add", description="Adds two integers.")
def add(a: int, b: int) -> int:
    """Returns the sum of two integers."""
    return a + b

if __name__ == "__main__":
    mcp.run(transport="sse")