# mcp_server.py

from fastmcp import MCPServer
from typing import Dict, Any

# ✅ Define MCPServer instance
mcp = MCPServer("SEO MCP")

# ✅ Register tools with decorator
@mcp.tool()
async def keywords(params: Dict[str, Any]) -> Dict[str, Any]:
    url = params.get("url")
    return {"keywords": [f"example-keyword-for-{url}"]}

@mcp.tool()
async def backlinks(params: Dict[str, Any]) -> Dict[str, Any]:
    return {"backlinks": ["site1.com", "site2.com"]}