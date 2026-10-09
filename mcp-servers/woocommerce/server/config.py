from pydantic_settings import BaseSettings, SettingsConfigDict

class MCPSettings(BaseSettings):
    SERVER_NAME: str = "woocommerce-mcp"
    PORT: int = 8001
    HOST: str = "0.0.0.0"

    # WooCommerce Store Credentials & URL
    WOOCOMMERCE_STORE_URL: str = "http://urumi-store-wordpress:80"
    WOOCOMMERCE_CONSUMER_KEY: str = ""
    WOOCOMMERCE_CONSUMER_SECRET: str = ""
    WOOCOMMERCE_VERIFY_SSL: bool = False

    # Internal Cluster Security (Gateway to MCP Server)
    INTERNAL_AUTH_TOKEN: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = MCPSettings()
