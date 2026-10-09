"""
WooCommerce Model Context Protocol (MCP) Server using Streamable HTTP (SSE).
Exposes tools for catalog management, product creation, order lookup, and status updates.
"""
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from server.config import settings
from server.client.woo_client import WooCommerceClient, WooCommerceAPIException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("woocommerce-mcp-server")

# Instantiate FastMCP server
mcp = FastMCP(
    name=settings.SERVER_NAME,
    instructions=(
        "WooCommerce MCP Server for Urumi AI Platform. "
        "Provides tools to query/manage WooCommerce products, check inventory, and inspect/update store orders."
    ),
    host=settings.HOST,
    port=settings.PORT,
)

# Shared WooCommerce client instance
woo_client = WooCommerceClient()

# =====================================================================
# 1. Product Tools
# =====================================================================

@mcp.tool()
async def list_products(
    page: int = 1,
    per_page: int = 10,
    search: str = "",
    category: str = "",
    status: str = "publish",
    min_price: str = "",
    max_price: str = "",
    stock_status: str = "",
) -> str:
    """
    List products from the WooCommerce store catalog with optional filtering and pagination.
    
    Args:
        page: Page number for pagination (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        search: Keyword search string matching title or description
        category: Category ID or slug to filter by
        status: Product status filter ('publish', 'draft', 'pending', 'private')
        min_price: Minimum price filter (e.g. '10.00')
        max_price: Maximum price filter (e.g. '100.00')
        stock_status: Stock status filter ('instock', 'outofstock', 'onbackorder')
    """
    try:
        products = await woo_client.list_products(
            page=page,
            per_page=per_page,
            search=search if search.strip() else None,
            category=category if category.strip() else None,
            status=status,
            min_price=min_price if min_price.strip() else None,
            max_price=max_price if max_price.strip() else None,
            stock_status=stock_status if stock_status.strip() else None,
        )
        
        results = []
        for p in products:
            results.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "sku": p.get("sku"),
                "price": p.get("price"),
                "regular_price": p.get("regular_price"),
                "sale_price": p.get("sale_price"),
                "status": p.get("status"),
                "stock_status": p.get("stock_status"),
                "stock_quantity": p.get("stock_quantity"),
                "categories": [c.get("name") for c in p.get("categories", [])],
                "permalink": p.get("permalink"),
            })
            
        return json.dumps({
            "count": len(results),
            "page": page,
            "products": results
        }, indent=2)
    except WooCommerceAPIException as e:
        logger.error(f"Error in list_products: {e}")
        return json.dumps({"error": str(e), "status_code": e.status_code})
    except Exception as e:
        logger.error(f"Unexpected error in list_products: {e}")
        return json.dumps({"error": f"Internal server error: {str(e)}"})


@mcp.tool()
async def create_product(
    name: str,
    regular_price: str,
    description: str = "",
    short_description: str = "",
    sku: str = "",
    manage_stock: bool = False,
    stock_quantity: int = 0,
    status: str = "publish",
) -> str:
    """
    Create a new product in the WooCommerce catalog.
    
    Args:
        name: The name of the product (Required)
        regular_price: Regular price of the product (Required, e.g. '29.99')
        description: Full product description (HTML or plain text)
        short_description: Brief product summary
        sku: Unique Stock Keeping Unit identifier
        manage_stock: Whether stock management is enabled at product level
        stock_quantity: Available inventory units (if manage_stock is True)
        status: Initial product status ('publish', 'draft', 'pending')
    """
    try:
        product_payload = {
            "name": name,
            "type": "simple",
            "regular_price": regular_price,
            "description": description,
            "short_description": short_description,
            "status": status,
        }
        if sku.strip():
            product_payload["sku"] = sku.strip()
        if manage_stock:
            product_payload["manage_stock"] = True
            product_payload["stock_quantity"] = stock_quantity

        created = await woo_client.create_product(product_payload)
        
        return json.dumps({
            "success": True,
            "message": "Product created successfully",
            "product": {
                "id": created.get("id"),
                "name": created.get("name"),
                "sku": created.get("sku"),
                "price": created.get("price"),
                "status": created.get("status"),
                "permalink": created.get("permalink"),
            }
        }, indent=2)
    except WooCommerceAPIException as e:
        logger.error(f"Error in create_product: {e}")
        return json.dumps({"error": str(e), "status_code": e.status_code})
    except Exception as e:
        logger.error(f"Unexpected error in create_product: {e}")
        return json.dumps({"error": f"Internal server error: {str(e)}"})


# =====================================================================
# 2. Order Tools
# =====================================================================

@mcp.tool()
async def list_orders(
    page: int = 1,
    per_page: int = 10,
    status: str = "",
    customer_id: int = 0,
    search: str = "",
) -> str:
    """
    List customer orders from WooCommerce with filtering and pagination.
    
    Args:
        page: Page number for pagination (default: 1)
        per_page: Number of orders per page (default: 10, max: 100)
        status: Filter by order status ('pending', 'processing', 'on-hold', 'completed', 'cancelled', 'refunded', 'failed')
        customer_id: Filter orders by specific customer ID (0 for all)
        search: Search term matching order number, billing details, or customer name
    """
    try:
        orders = await woo_client.list_orders(
            page=page,
            per_page=per_page,
            status=status if status.strip() else None,
            customer=customer_id if customer_id > 0 else None,
            search=search if search.strip() else None,
        )
        
        results = []
        for o in orders:
            items_summary = [
                f"{item.get('name')} x{item.get('quantity')}" 
                for item in o.get("line_items", [])
            ]
            billing = o.get("billing", {})
            results.append({
                "id": o.get("id"),
                "number": o.get("number"),
                "status": o.get("status"),
                "total": o.get("total"),
                "currency": o.get("currency"),
                "date_created": o.get("date_created"),
                "customer": {
                    "id": o.get("customer_id"),
                    "name": f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip(),
                    "email": billing.get("email"),
                },
                "items_count": len(o.get("line_items", [])),
                "items_summary": items_summary,
            })
            
        return json.dumps({
            "count": len(results),
            "page": page,
            "orders": results
        }, indent=2)
    except WooCommerceAPIException as e:
        logger.error(f"Error in list_orders: {e}")
        return json.dumps({"error": str(e), "status_code": e.status_code})
    except Exception as e:
        logger.error(f"Unexpected error in list_orders: {e}")
        return json.dumps({"error": f"Internal server error: {str(e)}"})


@mcp.tool()
async def get_order(order_id: int) -> str:
    """
    Retrieve comprehensive details for a single WooCommerce order by its order ID.
    
    Args:
        order_id: The unique numeric ID of the order (Required)
    """
    try:
        order = await woo_client.get_order(order_id)
        
        line_items = [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "product_id": item.get("product_id"),
                "variation_id": item.get("variation_id"),
                "quantity": item.get("quantity"),
                "subtotal": item.get("subtotal"),
                "total": item.get("total"),
                "sku": item.get("sku"),
                "price": item.get("price"),
            }
            for item in order.get("line_items", [])
        ]
        
        return json.dumps({
            "id": order.get("id"),
            "number": order.get("number"),
            "status": order.get("status"),
            "currency": order.get("currency"),
            "date_created": order.get("date_created"),
            "date_modified": order.get("date_modified"),
            "total": order.get("total"),
            "discount_total": order.get("discount_total"),
            "shipping_total": order.get("shipping_total"),
            "total_tax": order.get("total_tax"),
            "payment_method": order.get("payment_method_title"),
            "billing": order.get("billing"),
            "shipping": order.get("shipping"),
            "line_items": line_items,
            "customer_note": order.get("customer_note"),
        }, indent=2)
    except WooCommerceAPIException as e:
        logger.error(f"Error in get_order (ID={order_id}): {e}")
        return json.dumps({"error": str(e), "status_code": e.status_code})
    except Exception as e:
        logger.error(f"Unexpected error in get_order: {e}")
        return json.dumps({"error": f"Internal server error: {str(e)}"})


@mcp.tool()
async def update_order_status(order_id: int, status: str) -> str:
    """
    Update the processing status of a WooCommerce order.
    
    Args:
        order_id: The unique numeric ID of the order (Required)
        status: The target status ('pending', 'processing', 'on-hold', 'completed', 'cancelled', 'refunded', 'failed')
    """
    valid_statuses = {"pending", "processing", "on-hold", "completed", "cancelled", "refunded", "failed", "trash"}
    clean_status = status.strip().lower()
    
    if clean_status not in valid_statuses:
        return json.dumps({
            "error": f"Invalid status '{status}'. Allowed statuses: {', '.join(sorted(valid_statuses))}"
        })

    try:
        updated = await woo_client.update_order_status(order_id, clean_status)
        return json.dumps({
            "success": True,
            "message": f"Order #{order_id} status updated to '{clean_status}'",
            "order": {
                "id": updated.get("id"),
                "status": updated.get("status"),
                "date_modified": updated.get("date_modified"),
            }
        }, indent=2)
    except WooCommerceAPIException as e:
        logger.error(f"Error in update_order_status (ID={order_id}): {e}")
        return json.dumps({"error": str(e), "status_code": e.status_code})
    except Exception as e:
        logger.error(f"Unexpected error in update_order_status: {e}")
        return json.dumps({"error": f"Internal server error: {str(e)}"})


# =====================================================================
# Server Startup (Streamable HTTP / SSE)
# =====================================================================
if __name__ == "__main__":
    logger.info(f"Starting WooCommerce MCP Server on {settings.HOST}:{settings.PORT} via Streamable HTTP (SSE)...")
    mcp.run(transport="sse")
