# Urumi AI - FDE Internship Project Architecture

An enterprise-ready AI Forward Deployed Engineering (FDE) platform integrating conversational agents with e-commerce operations (WooCommerce) via the Model Context Protocol (MCP).

---

## 🛠 Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Dashboard** | React 18 + Vite + TypeScript | Merchant & Agent Operations Dashboard |
| **API Gateway** | FastAPI (Python 3.11+) | Agent orchestration, session state, REST/WS APIs |
| **MCP Server** | Python MCP SDK (`mcp`) | WooCommerce tools, resources, and SSE server |
| **Infrastructure** | Helm 3 + Kubernetes + Docker | Production orchestration, ingress, multi-environment configs |

---

## 📁 Project Directory Structure

```text
Urumi/
├── README.md                          # Project overview and architecture index
├── docker-compose.yml                 # Local multi-service orchestration
├── .gitignore                         # Python, Node, & build ignore patterns
├── docs/                              # Architecture & Technical Specifications
│   ├── ARCHITECTURE.md                # System design, dataflow & sequence diagrams
│   └── MCP_SPECIFICATION.md           # MCP tools, resources, and protocols spec
├── dashboard/                         # React + Vite Frontend
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── src/
│       ├── App.tsx
│       ├── index.css
│       └── main.tsx
├── gateway/                           # FastAPI API Gateway & Agent Orchestrator
│   ├── requirements.txt
│   ├── Dockerfile
│   └── app/
│       ├── main.py
│       ├── core/                      # Config & application settings
│       ├── api/v1/                    # Health, Chat, and WooCommerce endpoints
│       ├── agents/                    # LLM orchestration & tool calling loop
│       ├── mcp/                       # MCP Client connector (SSE/Stdio)
│       └── schemas/                   # Pydantic models
├── mcp-servers/
│   └── woocommerce/                   # WooCommerce MCP Server (Python MCP SDK)
│       ├── requirements.txt
│       ├── Dockerfile
│       └── server/
│           ├── server.py              # FastMCP Server & tool definitions
│           ├── config.py              # WooCommerce credentials config
│           └── client/
│               └── woo_client.py      # Async WooCommerce REST API client
└── helm/
    └── urumi-platform/                # Kubernetes Helm Charts
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── _helpers.tpl
            ├── gateway-deployment.yaml
            ├── gateway-service.yaml
            ├── mcp-woocommerce-deployment.yaml
            ├── mcp-woocommerce-service.yaml
            ├── dashboard-deployment.yaml
            ├── dashboard-service.yaml
            └── ingress.yaml
```

---

## 🚀 Quickstart (Local Scaffolding)

### 1. Run all services with Docker Compose
```bash
docker compose up --build
```
- Dashboard: `http://localhost:3000`
- FastAPI Gateway Docs: `http://localhost:8000/docs`
- WooCommerce MCP Server (SSE): `http://localhost:8001/sse`

### 2. Deploy to Kubernetes with Helm
```bash
helm install urumi-platform ./helm/urumi-platform -f ./helm/urumi-platform/values.yaml
```

---

## 📖 Documentation Links
- [System Architecture Specification](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/docs/ARCHITECTURE.md)
- [Model Context Protocol (MCP) Specification](file:///c:/Users/rayin/OneDrive/Desktop/Urumi/docs/MCP_SPECIFICATION.md)
