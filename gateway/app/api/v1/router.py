from fastapi import APIRouter
from app.api.v1 import health, chat, woocommerce

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(woocommerce.router, prefix="/woocommerce", tags=["woocommerce"])
