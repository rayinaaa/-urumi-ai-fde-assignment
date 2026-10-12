# Urumi AI - FDE Internship Assignment Submission

[![Urumi AI CI Pipeline](https://github.com/rayinaaa/-urumi-ai-fde-assignment/actions/workflows/ci.yml/badge.svg)](https://github.com/rayinaaa/-urumi-ai-fde-assignment/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/Release-v1.0.0-blue.svg)](https://github.com/rayinaaa/-urumi-ai-fde-assignment/releases/tag/v1.0.0)

This repository contains the complete implementation for the **Urumi AI Forward Deployed Engineering (FDE) Internship Assignment**.

---

## 🚀 Key Deliverables Summary

### 1. **WooCommerce Kubernetes Helm Stack** ([`helm/woocommerce/`](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/helm/woocommerce/))
- **WordPress 6.5** & **WooCommerce** with dynamic memory configuration and init hooks.
- **MySQL 8.0** with separate persistent volume storage.
- **Persistent Volume Claims (PVCs)** for both `/var/www/html/wp-content` and `/var/lib/mysql`.
- **Kubernetes Secrets** for secure database passwords, WordPress admin, and WooCommerce REST API keys.
- **Health Probes**: Liveness and readiness HTTP probes on `/wp-login.php` (WordPress) and TCP socket probes on port `3306` (MySQL).
- **Resource Requests and Limits** defined across all deployment templates.
- **Ingress Controller** configuration with TLS cert-manager annotations and payload buffer tuning.
- **Multi-Environment Profiles**:
  - [`values-local.yaml`](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/helm/woocommerce/values-local.yaml) for Minikube/Docker Desktop/Kind.
  - [`values-prod.yaml`](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/helm/woocommerce/values-prod.yaml) for production EKS/GKE/AKS with gp3 storage and TLS.

### 2. **Custom WooCommerce MCP Server** ([`mcp-servers/woocommerce/`](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/mcp-servers/woocommerce/))
- Built with the official **Python MCP SDK (`mcp` FastMCP)**.
- Operates over **Streamable HTTP (SSE)** on port `8001`.
- Communicates directly with the WooCommerce REST API (`/wp-json/wc/v3/`) using asynchronous `httpx`.
- Exposes the 5 required tools:
  1. `list_products` (catalog search, pagination, price and category filters)
  2. `create_product` (creates new product with SKU, pricing, and stock tracking)
  3. `list_orders` (queries store orders with status and customer filters)
  4. `get_order` (detailed order breakdown, line items, and shipping info)
  5. `update_order_status` (updates fulfillment state e.g. processing -> completed)
- **Kubernetes Isolation**: Enforced by [`mcp-network-policy.yaml`](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/helm/urumi-platform/templates/mcp-network-policy.yaml) so that the MCP server is strictly reachable **only** from the Gateway pod inside Kubernetes.

### 3. **FastAPI Agent Gateway** ([`gateway/`](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/gateway/))
- Act as the **MCP Host & Client** connecting to the WooCommerce MCP Server.
- Implements the agent reasoning loop with tool execution trace capture.
- Supports both standard JSON REST endpoints (`/api/v1/chat/message`) and Server-Sent Events token streaming (`/api/v1/chat/stream`).

### 4. **React + Vite Dashboard** ([`dashboard/`](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/dashboard/))
- **Live Agent Playground**: Chat with the store assistant, observe real-time tool execution traces, execution latency, and arguments.
- **Product Catalog View**: Live product inventory with an interactive "+ Add Product" modal calling MCP tools.
- **Orders Hub**: Interactive order management with inline status dropdowns.
- **MCP Mesh Inspector**: Real-time diagnostic monitor displaying registered tools, schemas, and network policies.

---

## ⚡ How to Run & Verify

### Option A: Quickstart with Docker Compose (All Services)
```bash
docker compose up --build
```
- **Dashboard UI**: `http://localhost:3000`
- **FastAPI Gateway & Swagger Docs**: `http://localhost:8000/docs`
- **WooCommerce MCP Server**: `http://localhost:8001/sse`

---

### Option B: Deploy to Kubernetes with Helm

#### 1. Deploy WooCommerce Store Stack
```bash
# Local environment
helm install urumi-store ./helm/woocommerce -f ./helm/woocommerce/values-local.yaml

# Production environment
helm install urumi-store ./helm/woocommerce -f ./helm/woocommerce/values-prod.yaml
```

#### 2. Deploy Urumi Platform (Gateway + Dashboard + MCP Server)
```bash
helm install urumi-platform ./helm/urumi-platform -f ./helm/urumi-platform/values.yaml
```

---

### Option C: Run Automated Pytest Suite
```bash
pytest
```
- Tests all 5 WooCommerce MCP tools with async mock fixtures.
- Tests Gateway health, chat, and MCP tool proxy endpoints.

---

## 📚 Architectural Documentation Links
- [System Architecture Specification](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/docs/ARCHITECTURE.md)
- [MCP Server Tool & Protocol Specification](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/docs/MCP_SPECIFICATION.md)
- [WooCommerce Kubernetes Deployment Guide](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/docs/WOOCOMMERCE_K8S_DEPLOYMENT.md)
