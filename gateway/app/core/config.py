from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Urumi AI Gateway"
    API_V1_STR: str = "/api/v1"
    
    # MCP WooCommerce Server Endpoint
    MCP_WOOCOMMERCE_URL: str = "http://localhost:8001/sse"
    
    # Redis Session Store
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_MODEL: str = "gpt-4o"
    
    # Security & CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
