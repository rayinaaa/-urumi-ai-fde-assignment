# Model Context Protocol (MCP) Specification - WooCommerce Server

## 1. Overview & Transport
The WooCommerce MCP Server is implemented using the Python MCP SDK (`mcp` FastMCP) and communicates over **Streamable HTTP (Server-Sent Events / SSE)**.
- **SSE Transport Endpoint**: `http://<service-name>:8001/sse`
- **Messages Endpoint**: `http://<service-name>:8001/messages/`
- **Cluster Isolation**: Reachable **only** from the FastAPI Gateway via Kubernetes `NetworkPolicy` and `ClusterIP` routing.

---

## 2. Implemented Tools

### 1. `list_products`
Lists products from the WooCommerce catalog with filtering and pagination.

**Input Parameters:**
- `page` (integer, default: 1): Page index.
- `per_page` (integer, default: 10, max: 100): Page size.
- `search` (string, optional): Search keyword.
- `category` (string, optional): Category slug/ID filter.
- `status` (string, default: "publish"): Product status.
- `min_price` (string, optional): Lower price limit.
- `max_price` (string, optional): Upper price limit.
- `stock_status` (string, optional): `instock`, `outofstock`, `onbackorder`.

**Returns:**
```json
{
  "count": 2,
  "page": 1,
  "products": [
    {
      "id": 101,
      "name": "Classic T-Shirt",
      "sku": "TSHIRT-001",
      "price": "24.99",
      "regular_price": "29.99",
      "sale_price": "24.99",
      "status": "publish",
      "stock_status": "instock",
      "stock_quantity": 50,
      "categories": ["Apparel", "Men"],
      "permalink": "https://store.local/product/classic-t-shirt"
    }
  ]
}
```

---

### 2. `create_product`
Creates a new product item in the WooCommerce catalog.

**Input Parameters:**
- `name` (string, required): Product name.
- `regular_price` (string, required): Regular price (e.g. `"29.99"`).
- `description` (string, optional): Detailed HTML/text description.
- `short_description` (string, optional): Brief excerpt summary.
- `sku` (string, optional): Stock Keeping Unit.
- `manage_stock` (boolean, default: false): Enable stock tracking.
- `stock_quantity` (integer, default: 0): Available inventory count.
- `status` (string, default: "publish"): Product status (`"publish"`, `"draft"`).

**Returns:**
```json
{
  "success": true,
  "message": "Product created successfully",
  "product": {
    "id": 102,
    "name": "Wireless Headphones",
    "sku": "AUDIO-WH-01",
    "price": "89.00",
    "status": "publish",
    "permalink": "https://store.local/product/wireless-headphones"
  }
}
```

---

### 3. `list_orders`
Lists customer orders with filtering by status, customer, or search terms.

**Input Parameters:**
- `page` (integer, default: 1): Page index.
- `per_page` (integer, default: 10, max: 100): Page size.
- `status` (string, optional): Order status (`pending`, `processing`, `on-hold`, `completed`, `cancelled`, `refunded`, `failed`).
- `customer_id` (integer, optional): Filter by customer ID.
- `search` (string, optional): Search keyword matching billing name/email/order#.

**Returns:**
```json
{
  "count": 1,
  "page": 1,
  "orders": [
    {
      "id": 501,
      "number": "501",
      "status": "processing",
      "total": "49.98",
      "currency": "USD",
      "date_created": "2026-10-08T18:00:00",
      "customer": {
        "id": 12,
        "name": "John Doe",
        "email": "john@example.com"
      },
      "items_count": 2,
      "items_summary": ["Classic T-Shirt x2"]
    }
  ]
}
```

---

### 4. `get_order`
Fetches complete order details, line items, billing/shipping addresses, and totals.

**Input Parameters:**
- `order_id` (integer, required): Unique order ID.

**Returns:**
```json
{
  "id": 501,
  "number": "501",
  "status": "processing",
  "currency": "USD",
  "date_created": "2026-10-08T18:00:00",
  "date_modified": "2026-10-08T18:15:00",
  "total": "49.98",
  "discount_total": "0.00",
  "shipping_total": "5.00",
  "total_tax": "4.00",
  "payment_method": "Credit Card (Stripe)",
  "billing": {
    "first_name": "John",
    "last_name": "Doe",
    "address_1": "123 Market St",
    "city": "San Francisco",
    "state": "CA",
    "postcode": "94105",
    "country": "US",
    "email": "john@example.com",
    "phone": "555-0199"
  },
  "shipping": {
    "first_name": "John",
    "last_name": "Doe",
    "address_1": "123 Market St",
    "city": "San Francisco",
    "state": "CA",
    "postcode": "94105",
    "country": "US"
  },
  "line_items": [
    {
      "id": 12,
      "name": "Classic T-Shirt",
      "product_id": 101,
      "variation_id": 0,
      "quantity": 2,
      "subtotal": "40.98",
      "total": "40.98",
      "sku": "TSHIRT-001",
      "price": 20.49
    }
  ],
  "customer_note": ""
}
```

---

### 5. `update_order_status`
Updates the fulfillment/processing status of an order.

**Input Parameters:**
- `order_id` (integer, required): Unique order ID.
- `status` (string, required): New status (`pending`, `processing`, `on-hold`, `completed`, `cancelled`, `refunded`, `failed`).

**Returns:**
```json
{
  "success": true,
  "message": "Order #501 status updated to 'completed'",
  "order": {
    "id": 501,
    "status": "completed",
    "date_modified": "2026-10-08T18:30:00"
  }
}
```

---

## 3. Kubernetes Security & Isolation Architecture

```mermaid
graph LR
    subgraph PublicNet ["External Network"]
        Browser["User / Merchant Browser"]
    end

    subgraph K8sCluster ["Kubernetes Cluster"]
        Ingress["Ingress Controller"]
        GatewayPod["FastAPI Gateway Pods\n(app=gateway)"]
        MCPServerPod["WooCommerce MCP Server Pods\n(app=mcp-woocommerce)"]
        WooPod["WordPress / WooCommerce Store Pods"]
        
        NetworkPolicy{{"NetworkPolicy:\nmcp-isolation\n(Only Gateway Ingress allowed)"}}
    end

    Browser -->|Public Ingress| Ingress
    Ingress -->|Route /api| GatewayPod
    GatewayPod -->|SSE Stream :8001| NetworkPolicy
    NetworkPolicy --> MCPServerPod
    MCPServerPod -->|REST API :80| WooPod

    Browser -.x|BLOCKED (No Ingress / Drop)| MCPServerPod
```
