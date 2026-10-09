import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_gateway_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_gateway_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["gateway"] == "online"

@pytest.mark.asyncio
async def test_gateway_chat_message():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat/message",
            json={"session_id": "test-session", "message": "Search products for chair"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session"
        assert "reply" in data
        assert len(data["traces"]) > 0
        assert data["traces"][0]["tool"] == "list_products"

@pytest.mark.asyncio
async def test_gateway_woocommerce_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/woocommerce/status")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert "list_products" in data["tools"]
