from fastapi import APIRouter
from app.mcp.client import mcp_client

router = APIRouter()

@router.get("/status")
async def get_store_status():
    """Returns WooCommerce connection status and loaded MCP tools."""
    tools = await mcp_client.list_tools()
    is_connected = await mcp_client.check_connection()
    return {
        "connected": True,
        "mcp_server_reachable": is_connected,
        "mcp_server_url": mcp_client.server_url,
        "tools_count": len(tools),
        "tools": [t["name"] for t in tools]
    }

@router.get("/products")
async def get_products(page: int = 1, per_page: int = 10, search: str = ""):
    """Proxy endpoint to query products via WooCommerce MCP tool."""
    return await mcp_client.call_tool("list_products", {"page": page, "per_page": per_page, "search": search})

@router.get("/orders")
async def get_orders(page: int = 1, per_page: int = 10, status: str = ""):
    """Proxy endpoint to query orders via WooCommerce MCP tool."""
    return await mcp_client.call_tool("list_orders", {"page": page, "per_page": per_page, "status": status})
