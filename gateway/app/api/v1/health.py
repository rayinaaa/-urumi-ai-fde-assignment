import os
from fastapi import APIRouter
from app.core.config import settings
from app.mcp.client import mcp_client

router = APIRouter()

@router.get("/")
async def health_check():
    mcp_alive = await mcp_client.check_connection()
    has_llm_key = bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or os.getenv("OPENAI_API_KEY"))
    return {
        "status": "healthy",
        "gateway": "online",
        "mcp_server": {
            "url": mcp_client.server_url,
            "connected": mcp_alive
        },
        "llm_provider": "openai" if settings.OPENAI_API_KEY else ("anthropic" if settings.ANTHROPIC_API_KEY else "smart-router"),
        "ready": True
    }
