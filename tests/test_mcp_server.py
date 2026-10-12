import pytest
import json
from unittest.mock import AsyncMock, patch

from server.client.woo_client import WooCommerceAPIException
import server.server as srv

@pytest.mark.asyncio
async def test_list_products_tool():
    mock_products = [
        {
            "id": 101,
            "name": "Test Chair",
            "sku": "CHAIR-01",
            "price": "199.99",
            "regular_price": "199.99",
            "sale_price": "",
            "status": "publish",
            "stock_status": "instock",
            "stock_quantity": 10,
            "categories": [{"name": "Office"}],
            "permalink": "http://store.local/test-chair"
        }
    ]
    with patch.object(srv.woo_client, "list_products", new=AsyncMock(return_value=mock_products)):
        res_json = await srv.list_products(search="chair")
        res = json.loads(res_json)
        assert res["count"] == 1
        assert res["products"][0]["name"] == "Test Chair"
        assert res["products"][0]["sku"] == "CHAIR-01"

@pytest.mark.asyncio
async def test_create_product_tool():
    mock_created = {
        "id": 105,
        "name": "New Desk",
        "sku": "DESK-01",
        "price": "299.00",
        "status": "publish",
        "permalink": "http://store.local/new-desk"
    }
    with patch.object(srv.woo_client, "create_product", new=AsyncMock(return_value=mock_created)):
        res_json = await srv.create_product(name="New Desk", regular_price="299.00", sku="DESK-01")
        res = json.loads(res_json)
        assert res["success"] is True
        assert res["product"]["id"] == 105
        assert res["product"]["sku"] == "DESK-01"

@pytest.mark.asyncio
async def test_list_orders_tool():
    mock_orders = [
        {
            "id": 501,
            "number": "501",
            "status": "processing",
            "total": "199.99",
            "currency": "USD",
            "date_created": "2026-10-08T18:00:00",
            "customer_id": 14,
            "billing": {"first_name": "John", "last_name": "Doe", "email": "john@example.com"},
            "line_items": [{"name": "Test Chair", "quantity": 1}]
        }
    ]
    with patch.object(srv.woo_client, "list_orders", new=AsyncMock(return_value=mock_orders)):
        res_json = await srv.list_orders()
        res = json.loads(res_json)
        assert res["count"] == 1
        assert res["orders"][0]["id"] == 501
        assert res["orders"][0]["status"] == "processing"

@pytest.mark.asyncio
async def test_get_order_tool():
    mock_order = {
        "id": 501,
        "number": "501",
        "status": "processing",
        "total": "199.99",
        "currency": "USD",
        "date_created": "2026-10-08T18:00:00",
        "date_modified": "2026-10-08T18:10:00",
        "discount_total": "0.00",
        "shipping_total": "0.00",
        "total_tax": "0.00",
        "payment_method_title": "Credit Card",
        "billing": {"first_name": "John", "last_name": "Doe"},
        "shipping": {"city": "San Francisco"},
        "line_items": [{"id": 1, "name": "Test Chair", "product_id": 101, "quantity": 1, "price": 199.99}],
        "customer_note": ""
    }
    with patch.object(srv.woo_client, "get_order", new=AsyncMock(return_value=mock_order)):
        res_json = await srv.get_order(order_id=501)
        res = json.loads(res_json)
        assert res["id"] == 501
        assert res["total"] == "199.99"

@pytest.mark.asyncio
async def test_update_order_status_tool():
    mock_updated = {
        "id": 501,
        "status": "completed",
        "date_modified": "2026-10-08T18:30:00"
    }
    with patch.object(srv.woo_client, "update_order_status", new=AsyncMock(return_value=mock_updated)):
        res_json = await srv.update_order_status(order_id=501, status="completed")
        res = json.loads(res_json)
        assert res["success"] is True
        assert res["order"]["status"] == "completed"
